# \data

## `├── \external`

The data collected from third party sources.

## `├── \interim`

Intermediate data transformations.

## `├── \metadata`

Special metadata files the describe the data files individually or collectively.

## `├── \processed`

Final processed data which is further subdivided.

### `│  ├── \test`

Data for the final model testing.

### `│  ├── \train`

Data for model training.

### `│  └── \val`

Data for model validation.

## `└── \raw`

Raw source data, immutable.
