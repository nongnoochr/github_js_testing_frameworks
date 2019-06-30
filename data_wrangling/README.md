# Data Wrangling

## Package json analysis
* Data of repo which contains package.json that contains one of the interested JS Testing framework is extracted via **BigQuery**
  * See this [kaggle](https://www.kaggle.com/nongnoochr/bq-github-package-deps) for detailed steps
  * The exported csv data from this [kaggle](https://www.kaggle.com/nongnoochr/bq-github-package-deps) is used for this analysis (and it was saved to data/github_package_deps_June_2019.csv)
* Data of GitHub repositories were retrieved using GitHub **GraphQL** and **REST** apis.
  * Data saved to data/github_repo_for package_deps_June_2019.csv
  * See details of how data was collected in the notebook **[collect_repo_info.ipynb](./collect_repo_info.ipynb)**