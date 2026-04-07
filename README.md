# TravelBuddy — Trợ lý Du lịch Thông minh

Agent tư vấn du lịch nội địa Việt Nam, xây dựng bằng LangGraph + OpenAI. Tự động tìm chuyến bay, khách sạn và tính ngân sách dựa trên yêu cầu của người dùng.

## Cấu trúc

```
lab4_agent/
├── agent.py          # LangGraph graph + chat loop
├── tools.py          # 4 tools: search_flights, search_hotels, calculate_budget, format_response
├── system_prompt.txt # Persona, rules, constraints cho LLM
├── test/             # Unit test cho từng tool
└── agent.log         # Log runtime (tự sinh, không commit)
```

## Cài đặt

```bash
pip install langchain langchain-openai langgraph python-dotenv
```

Tạo file `.env`:
```
OPENAI_API_KEY=your_key_here
```

## Chạy

```bash
python agent.py
```

## Tools

| Tool | Chức năng |
|---|---|
| `search_flights` | Tìm chuyến bay theo điểm đi / điểm đến |
| `search_hotels` | Tìm khách sạn theo thành phố, lọc theo giá tối đa |
| `calculate_budget` | Tính tổng chi phí, so sánh với ngân sách |
| `format_response` | Format kết quả tư vấn (luôn là tool cuối cùng, do graph enforce) |

## Luồng hoạt động

Graph LangGraph với 2 node (`agent`, `tools`) và routing có điều kiện:

```
                        ┌─────────────────────────────────────────┐
                        │                                         │
                        ▼                                         │
              ┌─────────────────┐                                 │
   START ───► │      agent      │                                 │
              └────────┬────────┘                                 │
                       │                                          │
              tools_condition                                     │
             /                  \                                 │
     (có tool call)       (không tool call)                       │
            │                    │                                │
            ▼                    ▼                                │
   ┌─────────────────┐          END                               │
   │      tools      │                                            │
   └────────┬────────┘                                            │
            │                                                     │
   after_tools_condition                                          │
      /              \                                            │
(format_response    (tool khác)                                   │
   được gọi)            │                                         │
      │                 └─────────────────────────────────────────┘
      ▼
     END
```

**Nodes:**
- `agent` — gọi LLM với tools bound, quyết định tool nào cần gọi
- `tools` — thực thi tool call(s) từ LLM

**Edges:**
- `START → agent` — bắt đầu mỗi lượt hội thoại
- `agent → tools_condition` — nếu LLM có tool call thì sang `tools`, ngược lại về `END`
- `tools → after_tools_condition` — nếu `format_response` vừa được gọi thì về `END`, ngược lại quay lại `agent`

`format_response` được enforce là node kết thúc **ở tầng graph** — không phụ thuộc vào system prompt.

## Test cases

| # | Input | Kỳ vọng |
|---|---|---|
| 1 | Chào hỏi chung | Trả lời trực tiếp, không gọi tool |
| 2 | Tìm vé Hà Nội → Đà Nẵng | Gọi `search_flights`, liệt kê 4 chuyến |
| 3 | Hà Nội → Phú Quốc, 2 đêm, 5 triệu | Tool chaining 3 bước + bảng ngân sách |
| 4 | "Tôi muốn đặt khách sạn" | Hỏi lại thành phố / ngân sách |
| 5 | Câu hỏi ngoài du lịch | Từ chối lịch sự |
