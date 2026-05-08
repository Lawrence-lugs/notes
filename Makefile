.PHONY: site clean generate

site: generate
	quarto render

generate:
	python3 scripts/collect_public_notes.py

clean:
	rm -rf notes/*
	rm -rf docs/*
