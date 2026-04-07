from math import inf
from typing import Union
from langchain_core.tools import tool

FLIGHTS_DB = {
    ("Hà Nội", "Đà Nẵng"): [
        {"airline": "Vietnam Airlines", "departure": "06:00", "arrival": "07:20", "price": 1_450_000, "class": "economy"},
        {"airline": "Vietnam Airlines", "departure": "14:00", "arrival": "15:20", "price": 2_800_000, "class": "business"},
        {"airline": "VietJet Air", "departure": "08:30", "arrival": "09:50", "price": 890_000, "class": "economy"},
        {"airline": "Bamboo Airways", "departure": "11:00", "arrival": "12:20", "price": 1_200_000, "class": "economy"},
    ],
    ("Hà Nội", "Phú Quốc"): [
        {"airline": "Vietnam Airlines", "departure": "07:00", "arrival": "09:15", "price": 2_100_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "10:00", "arrival": "12:15", "price": 1_350_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "16:00", "arrival": "18:15", "price": 1_100_000, "class": "economy"},
    ],
    ("Hà Nội", "Hồ Chí Minh"): [
        {"airline": "Vietnam Airlines", "departure": "06:00", "arrival": "08:10", "price": 1_600_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "07:30", "arrival": "09:40", "price": 950_000, "class": "economy"},
        {"airline": "Bamboo Airways", "departure": "12:00", "arrival": "14:10", "price": 1_300_000, "class": "economy"},
        {"airline": "Vietnam Airlines", "departure": "18:00", "arrival": "20:10", "price": 3_200_000, "class": "business"},
    ],
    ("Hồ Chí Minh", "Đà Nẵng"): [
        {"airline": "Vietnam Airlines", "departure": "09:00", "arrival": "10:20", "price": 1_300_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "13:00", "arrival": "14:20", "price": 780_000, "class": "economy"},
    ],
    ("Hồ Chí Minh", "Phú Quốc"): [
        {"airline": "Vietnam Airlines", "departure": "08:00", "arrival": "09:00", "price": 1_100_000, "class": "economy"},
        {"airline": "VietJet Air", "departure": "15:00", "arrival": "16:00", "price": 650_000, "class": "economy"},
    ],
}

HOTELS_DB = {
    "Đà Nẵng": [
        {"name": "Mường Thanh Luxury", "stars": 5, "price_per_night": 1_800_000, "area": "Mỹ Khê", "rating": 4.5},
        {"name": "Sala Danang Beach", "stars": 4, "price_per_night": 1_200_000, "area": "Mỹ Khê", "rating": 4.3},
        {"name": "Fivitel Danang", "stars": 3, "price_per_night": 650_000, "area": "Sơn Trà", "rating": 4.1},
        {"name": "Memory Hostel", "stars": 2, "price_per_night": 250_000, "area": "Hải Châu", "rating": 4.6},
        {"name": "Christina's Homestay", "stars": 2, "price_per_night": 350_000, "area": "An Thượng", "rating": 4.7},
    ],
    "Phú Quốc": [
        {"name": "Vinpearl Resort", "stars": 5, "price_per_night": 3_500_000, "area": "Bãi Dài", "rating": 4.4},
        {"name": "Sol by Meliá", "stars": 4, "price_per_night": 1_500_000, "area": "Bãi Trường", "rating": 4.2},
        {"name": "Lahana Resort", "stars": 3, "price_per_night": 800_000, "area": "Dương Đông", "rating": 4.0},
        {"name": "9Station Hostel", "stars": 2, "price_per_night": 200_000, "area": "Dương Đông", "rating": 4.5},
    ],
    "Hồ Chí Minh": [
        {"name": "Rex Hotel", "stars": 5, "price_per_night": 2_800_000, "area": "Quận 1", "rating": 4.3},
        {"name": "Liberty Central", "stars": 4, "price_per_night": 1_400_000, "area": "Quận 1", "rating": 4.1},
        {"name": "Cochin Zen Hotel", "stars": 3, "price_per_night": 550_000, "area": "Quận 3", "rating": 4.4},
        {"name": "The Common Room", "stars": 2, "price_per_night": 180_000, "area": "Quận 1", "rating": 4.6},
    ],
}

@tool
def search_flights(origin: str, destination: str) -> str:
    """Tìm kiếm các chuyến bay giữa hai thành phố
    Tham số:
    - origin: Thành phố khởi hành
    - destination: Thành phố đến
    Trả về danh sách chuyến bay với hãng, giờ bay, giá vé
    Nếu không có chuyến bay trả về thông báo không có chuyến bay 
    """ 

    def format_price(price):
        return f"{price:,.0f}".replace(",", ".").replace("_", ".") + " VNĐ"

    def format_flights(key, orig, dest):
        lines = [f"✈️  Các chuyến bay từ {orig} đến {dest}:\n"]
        for i, flight in enumerate(FLIGHTS_DB[key], 1):
            price_fmt = format_price(flight['price'])
            lines.append(
                f"  [{i}] {flight['airline']}\n"
                f"      Khởi hành: {flight['departure']}  →  Đến: {flight['arrival']}\n"
                f"      Hạng: {flight['class'].capitalize()}  |  Giá: {price_fmt}"
            )
        lines.append("\nVui lòng chọn chuyến bay phù hợp với bạn.")
        return "\n".join(lines)

    try:
        if (origin, destination) in FLIGHTS_DB:
            return format_flights((origin, destination), origin, destination)
        elif (destination, origin) in FLIGHTS_DB:
            return format_flights((destination, origin), destination, origin)
        else:
            return f"Không tìm thấy thông tin chuyến bay từ {origin} đến {destination}. Vui lòng kiểm tra lại điểm đến và điểm khởi hành."
    except Exception as e:
        return f"Lỗi khi tìm chuyến bay: {e}"

@tool
def search_hotels(city: str, max_price_per_night: Union[str, int, None] = 999999999) -> str:
    """Tìm kiếm các khách sạn tại một thành phố, có thể lọc theo giá tối đa mỗi đêm
    Tham số:
    - city: Thành phố cần tìm kiếm khách sạn (Ví dụ: "Đà Nẵng", "Phú Quốc", "Hồ Chí Minh")
    - max_price_per_night: Giá tối đa mỗi đêm (mặc định là không giới hạn VNĐ). Chấp nhận định dạng như "1.500.000", "1,500,000", "1 500 000", "1500000"
    Trả về danh sách khách sạn với tên, số sao, giá/đêm, khu vực, rating.
    Nếu không có khách sạn trả về thông báo không có khách sạn
    """ 

    def parse_price(value) -> int:
        if value is None:
            return inf
        if isinstance(value, (int, float)):
            return int(value)
        cleaned = str(value).replace(",", "").replace(".", "").replace(" ", "").replace("_", "")
        try:
            return int(cleaned)
        except ValueError:
            return inf

    max_price_per_night = parse_price(max_price_per_night)

    def format_price(price):
        return f"{price:,.0f}".replace(",", ".").replace("_", ".") + " VNĐ"

    def format_hotels(city, max_price_per_night):
        lines = [f"🏨  Các khách sạn tại {city}:\n"]
        for i, hotel in enumerate(HOTELS_DB[city], 1):
            if hotel['price_per_night'] > max_price_per_night:
                continue
            price_fmt = format_price(hotel['price_per_night'])
            lines.append(
                f"  [{i}] {hotel['name']}\n"
                f"     - Số sao: {hotel['stars']}\n"
                f"     - Giá mỗi đêm: {price_fmt}\n"
                f"     - Khu vực: {hotel['area']}\n"
                f"     - Rating: {hotel['rating']}"
            )
        lines.append("\nVui lòng chọn khách sạn phù hợp với bạn.")
        return "\n".join(lines)

    try:
        if city not in HOTELS_DB:
            return f"Không tìm thấy thông tin khách sạn tại {city}. Vui lòng kiểm tra lại thành phố."

        matching = [h for h in HOTELS_DB[city] if h['price_per_night'] <= max_price_per_night]
        if not matching:
            min_price = min(h['price_per_night'] for h in HOTELS_DB[city])
            return (
                f"Không tìm thấy khách sạn tại {city} với giá dưới {format_price(max_price_per_night)}. "
                f"Khách sạn rẻ nhất là {format_price(min_price)}. Hãy thử tăng ngân sách."
            )
        return format_hotels(city, max_price_per_night)
    except Exception as e:
        return f"Lỗi khi tìm khách sạn: {e}"

@tool
def calculate_budget(
    total_budget: Union[str, int, None] = None,
    expenses: Union[str, int, None] = None,
    flights_price: Union[str, int, None] = None,
    hotels_price: Union[str, int, None] = None,
) -> str:
    """Tính toán ngân sách còn lại sau khi trừ đi các khoản chi phí
    Tham số:
    - total_budget: Ngân sách tổng ban đầu (VNĐ)
    - expenses: Chuỗi mô tả các khoản chi phí cách nhau bởi dấu phẩy (VNĐ)
    định dạng 'tên_khoản:số tiền' VD:
    Ví dụ: 'Ăn uống: 100000, Đi taxi: 50000'
    Trả về chi tiết các khoản chi phí và ngân sách còn lại
    Nếu vượt quá ngân sách, trả về thông báo vượt ngân sách, cảnh báo số tiền còn thiếu
    """

    def parse_price(value) -> int:
        if value is None:
            return 0
        if isinstance(value, (int, float)):
            return int(value)
        cleaned = str(value).replace(",", "").replace(".", "").replace(" ", "").replace("_", "")
        try:
            return int(cleaned)
        except ValueError:
            raise ValueError(f"Không thể đọc số tiền: '{value}'")

    def format_price(amount: int) -> str:
        return f"{amount:,}".replace(",", ".")

    def parse_expenses(expenses_str: str) -> dict:
        import re
        result = {}
        # Tách theo pattern "tên: số_tiền" — dùng regex để không bị nhầm dấu , trong số tiền
        items = re.split(r",\s*(?=[^\d])", expenses_str)
        for item in items:
            item = item.strip()
            if not item:
                continue
            if ":" not in item:
                raise ValueError(f"Khoản chi '{item}' không đúng định dạng 'tên: số_tiền'")
            name, amount_str = item.split(":", 1)
            result[name.strip()] = parse_price(amount_str.strip())
        return result

    try:
        budget = parse_price(total_budget)
        expense_dict = parse_expenses(str(expenses)) if expenses else {}
    except ValueError as e:
        return f"Lỗi định dạng đầu vào: {e}"

    total_spent = sum(expense_dict.values())
    remaining = budget - total_spent

    lines = ["Bảng chi phí:"]
    for name, amount in expense_dict.items():
        lines.append(f"  - {name}: {format_price(amount)}đ")
    lines.append("  ---")
    lines.append(f"  Tổng chi:  {format_price(total_spent)}đ")
    lines.append(f"  Ngân sách: {format_price(budget)}đ")

    if remaining < 0:
        lines.append(f"  Còn lại:   -{format_price(abs(remaining))}đ")
        lines.append(f"\n  Vượt ngân sách {format_price(abs(remaining))} đồng! Cần điều chỉnh.")
    else:
        lines.append(f"  Còn lại:   {format_price(remaining)}đ")

    return "\n".join(lines)


@tool
def format_response(
    flights_info: str = "",
    hotels_info: str = "",
    budget_info: str = "",
    tips: str = "",
    closing_question: str = "",
) -> str:
    """Định dạng và trình bày kết quả tư vấn du lịch thành câu trả lời hoàn chỉnh.
    Gọi tool này SAU KHI đã thu thập đủ dữ liệu từ các tool khác.
    Tham số:
    - flights_info: Kết quả nguyên văn từ search_flights (để trống nếu chưa tìm)
    - hotels_info: Kết quả nguyên văn từ search_hotels (để trống nếu chưa tìm)
    - budget_info: Kết quả nguyên văn từ calculate_budget (để trống nếu không có ngân sách)
    - tips: 1–3 mẹo ngắn về thời tiết, ẩm thực hoặc tiết kiệm tại điểm đến, mỗi mẹo một dòng
    - closing_question: Câu hỏi ngắn thân thiện để tiếp tục hỗ trợ khách
    """
    sections: list[str] = []

    if flights_info:
        sections.append(f"CHUYEN BAY\n{flights_info}")

    if hotels_info:
        sections.append(f"KHACH SAN\n{hotels_info}")

    if budget_info:
        sections.append(f"TONG CHI PHI UOC TINH\n{budget_info}")

    if tips:
        sections.append(f"GOI Y THEM\n{tips}")

    body = "\n\n".join(sections)

    if closing_question:
        body = f"{body}\n\n{closing_question}"

    return body