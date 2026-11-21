"""Parse and aggregate SEC Form 13F information-table XML into JSON.

Usage (from the Next.js project root):
    python scripts/parse_13f_v2.py data/sec/berkshire_2026_q3.xml

Standard library only; does not download anything or overwrite your source XML.
The JSON keeps both individual SEC lines and aggregated security positions.
"""

from collections import defaultdict
from pathlib import Path
import json
import sys
import xml.etree.ElementTree as ET

SOURCE_URL = (
    "https://www.sec.gov/Archives/edgar/data/1067983/"
    "000119312526463399/60471.xml"
)
EXPECTED = {"raw_line_count": 89, "position_count": 30, "total_reported_value_usd": 304_196_581_325}


def local_name(tag):
    return tag.rsplit("}", 1)[-1]


def child(element, target):
    if element is None:
        return None
    return next((item for item in element if local_name(item.tag) == target), None)


def field(element, target):
    item = child(element, target)
    return (item.text or "").strip() if item is not None else ""


def integer(value):
    return int((value or "0").replace(",", ""))


def parse_13f(xml_file, out_file):
    xml_file = Path(xml_file)
    out_file = Path(out_file)
    if not xml_file.is_file():
        raise FileNotFoundError(f"找不到 XML 檔案: {xml_file.resolve()}")

    root = ET.parse(xml_file).getroot()
    tables = [el for el in root.iter() if local_name(el.tag) == "infoTable"]
    if not tables:
        raise ValueError("找不到 <infoTable>。請下載 SEC 13F information table XML，而非 primary_doc.xml。")

    raw_lines = []
    groups = {}
    for line_number, item in enumerate(tables, 1):
        quantity = child(item, "shrsOrPrnAmt")
        row = {
            "line_number": line_number,
            "issuer": field(item, "nameOfIssuer"),
            "security_class": field(item, "titleOfClass"),
            "cusip": field(item, "cusip").upper(),
            "figi": field(item, "figi") or None,
            "shares_or_principal": integer(field(quantity, "sshPrnamt")),
            "quantity_type": field(quantity, "sshPrnamtType"),
            "market_value_usd": integer(field(item, "value")),
            "put_call": field(item, "putCall") or None,
        }
        if not row["cusip"]:
            raise ValueError(f"第 {line_number} 筆沒有 CUSIP，停止以防錯誤合併。")
        raw_lines.append(row)
        # Match the same security and side; never merge options with common shares.
        # Keep different share classes / security types distinct.
        key = (row["cusip"], row["security_class"], row["quantity_type"], row["put_call"])
        if key not in groups:
            groups[key] = {
                "issuer": row["issuer"],
                "security_class": row["security_class"],
                "cusip": row["cusip"],
                "figi": row["figi"],
                "shares_or_principal": 0,
                "quantity_type": row["quantity_type"],
                "market_value_usd": 0,
                "put_call": row["put_call"],
                "source_line_count": 0,
            }
        entry = groups[key]
        entry["shares_or_principal"] += row["shares_or_principal"]
        entry["market_value_usd"] += row["market_value_usd"]
        entry["source_line_count"] += 1

    positions = list(groups.values())
    total = sum(line["market_value_usd"] for line in raw_lines)
    if total <= 0 or sum(p["market_value_usd"] for p in positions) != total:
        raise ValueError("加總驗證失敗，請檢查 XML。")
    for position in positions:
        position["portfolio_weight_pct"] = round(100 * position["market_value_usd"] / total, 4)
    positions.sort(key=lambda p: p["market_value_usd"], reverse=True)

    result = {
        "manager": "Berkshire Hathaway Inc.",
        "manager_cik": "0001067983",
        "report_period": "2026-09-30",
        "filing_date": "2026-11-16",
        "source_form": "13F-HR",
        "source_url": SOURCE_URL,
        "source_file": xml_file.name,
        "value_unit": "USD",
        "raw_line_count": len(raw_lines),
        "position_count": len(positions),
        "total_reported_value_usd": total,
        "holdings": positions,
        "raw_lines": raw_lines,
        "note": "13F quarter-end holdings, not acquisition cost or trade history. Positions are aggregated by CUSIP, security class, quantity type and put/call.",
    }
    out_file.parent.mkdir(parents=True, exist_ok=True)
    out_file.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"SEC XML 明細筆數: {len(raw_lines)}")
    print(f"合併後證券部位數: {len(positions)}")
    print(f"13F 總市值 (USD): ${total:,}")
    print(f"輸出檔案: {out_file.resolve()}")
    print("合併後前五大證券部位:")
    for p in positions[:5]:
        print(f"  {p['issuer']} [{p['cusip']}]: ${p['market_value_usd']:,} ({p['portfolio_weight_pct']:.2f}%), 合併 {p['source_line_count']} 筆")

    checks = {
        "raw_line_count": len(raw_lines),
        "position_count": len(positions),
        "total_reported_value_usd": total,
    }
    if checks == EXPECTED:
        print("PASS: 89 筆明細、30 個部位、$304,196,581,325，與 Berkshire 2026 Q3 申報摘要相符。")
    else:
        print("WARNING: 與 Berkshire 2026 Q3 預期摘要不同。請確認 XML 檔案版本與內容。")
        for name, expected in EXPECTED.items():
            if checks[name] != expected:
                print(f"  {name}: 實際 {checks[name]:,}；預期 {expected:,}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/parse_13f_v2.py data/sec/berkshire_2026_q3.xml")
        sys.exit(2)
    try:
        parse_13f(sys.argv[1], "data/real/berkshire_2026_q3.json")
    except (OSError, ValueError, ET.ParseError) as error:
        print(f"ERROR: {error}")
        sys.exit(1)
