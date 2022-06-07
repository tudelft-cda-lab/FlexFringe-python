# FlexFringe-python
Python wrapper for flexfringe

## Usage
```python
    from flexfringe import FlexFringe

    tracefile = "/path/to/your/tracefile"

    flexfringe = FlexFringe(
        "/path/to/flexfringe"
    )

    # Learn a state machine
    result = flexfringe.fit(
        tracefile,
        heuristic_name="alergia",
        data_name="alergia_data"
    )

    # Display the learned state machine
    flexfringe.show()

    # Use state machine to predict likelihoods
    df = flexfringe.predict(
        tracefile,
        heuristic_name="alergia",
        data_name="alergia_data"
    )

    print(df.head())
```

prints:
```
       abbadingo type abbadingo length  ... mean scores min score
row nr                                  ...                      
0                   1               10  ...    -2.00281  -2.80362
1                   1               14  ...    -2.57718  -2.80362
2                   1               27  ...    -2.39332  -3.69244
3                   1               25  ...    -2.32146  -3.62624
4                   1                7  ...    -2.15263  -3.07357

[5 rows x 8 columns]

Process finished with exit code 0

```