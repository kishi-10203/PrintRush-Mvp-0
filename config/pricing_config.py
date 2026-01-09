
"""
Pricing in context to INR 

pricing per page and per unit work in binding and etc --- Multiplier values here 

"""


class Pricing:
    # late night surcharge
    late_night_surcharge_per_order: float = 20.0 

    # A4 printing costs
    A4_black_and_white_print_cost_per_page: float = 2.0
    A4_color_print_cost_per_page: float = 10.0
    A4_glossy_print_cost_per_page: float = 15.0
    A4_bond_paper_print_cost_per_page: float = 15.0

    # A4 Double Sided printing costs
    A4_duplex_black_and_white_print_cost_per_page: float = 3.0
    A4_duplex_color_print_cost_per_page: float = 15.0

    #Binding
    soft_binding_cost_per_booklet: float = 40.0
    spiral_binding_cost_per_booklet: float = 50.0

    #Delivery
    delivery_charge_per_order: float = 0.0 # free delivery for now