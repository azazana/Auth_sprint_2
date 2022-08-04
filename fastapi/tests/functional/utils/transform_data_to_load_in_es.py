def transform_data_to_load(data, model, index):
    data_pydantic = [
        model(_id=item['id'], _index=index, **item)
        for item in data
    ]
    return [item.dict(by_alias=True) for item in data_pydantic]
