.PHONY: site clean generate

site: generate
	quarto render

generate:
	python3 scripts/batch_gfm_to_quarto.py _notes notes

clean:
	rm -rf notes/*
	rm -rf docs/*
