deps-petsc:
	bash install_all.sh

deps-arpack:
	bash install_all_with_arpack.sh

conda:
	conda build .

install:
	bash install.sh
	pip install -e .

