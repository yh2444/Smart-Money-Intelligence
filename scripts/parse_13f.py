"""Convert a locally downloaded SEC Form 13F information-table XML into JSON.

From the Next.js project root, run:
    python scripts/parse_13f.py data/sec/berkshire_2026_q3.xml

This script uses only Python's standard library.
"""

import json
import sys
from pathlib import Path
import xml.etree.ElementTree as ET

SOURCE_URL = (
    "https://www.sec.gov/Archives/edgar/data/1067983/"
    "000119312526463399/60471.xml"
)


def local_name(tag: str) -> str:
    """Strip a namespace (if any) from an XML element name."""
    return tag.rsplit("}", 1)[-1]


def child_text(parent: ET.Element | None, name: str) -> str | None:
    if parent is None:
        return None
    for child in parent:
        if local_name(child.tag) == name:
            return (child.text or "").strip() or None
    return None


def child_element(parent: ET.Element, name: str) -> ET.Element | None:
    for child in parent:
        if local_name(child.tag) == name:
            return child
    return None


def integer(text: str | None) -> int:
    if not text:
        return 0
    return int(text.replace(",", ""))


def convert(xml_path: Path, output_path: Path) -> None:
    if not xml_path.is_file():
        raise FileNotFoundError(f"找不到 XML 檔案: {xml_path.resolve()}")

    root = ET.parse(xml_path).getroot()
    rows = [element for element in root.iter() if local_name(element.tag) == "infoTable"]
    if not rows:
        raise ValueError(
            "沒有找到 <infoTable> 持股資料。請確認下載的是 60471.xml "
            "(INFORMATION TABLE)，不是 primary_doc.xml 或網頁 HTML。"
        )

    holdings = []
    for row in rows:
        qty_block = child_element(row, "shrsOrPrnAmt")
        holdings.append(
            {
                "issuer": child_text(row, "nameOfIssuer"),
                "security_class": child_text(row, "titleOfClass"),
                "cusip": child_text(row, "cusip"),
                "figi": child_text(row, "figi"),
                "shares_or_principal": integer(child_text(qty_block, "sshPrnamt")),
                "quantity_type": child_text(qty_block, "sshPrnamtType"),
                "market_value_usd": integer(child_text(row, "value")),
                "put_call": child_text(row, "putCall"),
            }
        )

    total_value = sum(item["market_value_usd"] for item in holdings)
    if total_value <= 0:
        raise ValueError("持股市值總和不是正數，請檢查來源 XML。")
    for item in holdings:
        item["portfolio_weight_pct"] = round(
            100 * item["market_value_usd"] / total_value, 4
        )

    holdings.sort(key=lambda item: item["market_value_usd"], reverse=True)
    data = {
        "manager": "Berkshire Hathaway Inc.",
        "manager_cik": "0001067983",
        "report_period": "2026-09-30",
        "filing_date": "2026-11-16",
        "source_form": "13F-HR",
        "source_url": SOURCE_URL,
        "source_file": xml_path.name,
        "value_unit": "USD (not USD thousands)",
        "position_count": len(holdings),
        "total_reported_value_usd": total_value,
        "holdings": holdings,
        "note": (
            "13F quarter-end holdings only. These figures are NOT acquisition cost, "
            "transaction history, or a complete portfolio. Ticker symbols are "
            "not included in the original 13F information table."
        ),
    }

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"Successfully parsed {len(holdings)} holdings")
    print(f"Total 13F reported value: ${total_value:,}")
    print(f"JSON saved to: {output_path.resolve()}")
    print("Top five holdings:")
    for item in holdings[:5]:
        print(
            f"  {item['issuer']}: ${item['market_value_usd']:,} "
            f"({item['portfolio_weight_pct']:.2f}%)"
        )
    if len(holdings) != 30 or total_value != 304_196_581_325:
        print(
            "NOTE: This does not match the expected 2026 Q3 Berkshire filing "
            "(30 positions, $304,196,581,325). Check the downloaded document."
        )


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/parse_13f.py data/sec/berkshire_2026_q3.xml")
        sys.exit(1)
    source = Path(sys.argv[1])
    destination = Path("data/real/berkshire_2026_q3.json")
    try:
        convert(source, destination)
    except (OSError, ValueError, ET.ParseError) as error:
        print(f"ERROR: {error}")
        sys.exit(1)
