import pandera as pa
from pandera import Column, DataFrameSchema, Check

product_schema = DataFrameSchema({
    "product_id": Column(int, Check.greater_than(0)),
    "name": Column(str, Check.str_length(min_value=1)),
    "price": Column(float, Check.greater_than_or_equal_to(0)),
    "stock": Column(int, Check.greater_than_or_equal_to(0)),
    "active": Column(bool)
})
