up:      ; docker compose up -d
data:    ; python -m src.generate_data
etl:     ; python -m src.etl
dash:    ; streamlit run dashboard/app.py
test:    ; pytest -q
all: up data etl
