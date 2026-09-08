.PHONY: setup generate clean

setup:
	pip install -r requirements.txt

generate:
	python -m data.generator.cli --scale $(scale) --seed $(seed)

clean:
	rm -rf data/generated/*
	rm -rf data/artifacts/*
	rm -rf data/manifests/*
