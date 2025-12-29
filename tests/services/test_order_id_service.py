from services.order_id_service import generate_order_id

def test_generate_order_id_real_notion():
    college_code = "HITS"

    order_id = generate_order_id(college_code)

    assert order_id.startswith(college_code)
    assert len(order_id) == len(college_code) + 4

    print("Generated order ID:", order_id)
