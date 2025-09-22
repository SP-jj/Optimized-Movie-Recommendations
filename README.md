 # Optimized-Movie-Recommendations

This project uses a Kaggle dataset.  
**Note**: The dataset itself is *not included* in this repo because of Kaggle’s license terms.

---

## Setup

1. Clone this repo:
   ```bash
   git clone https://github.com/SP-jj/Optimized-Movie-Recommendations.git
   cd Optimized-Movie-Recommendations

2. Install Requirements:
	pip install -r requirements.txt

3. Authenticate Kaggle:
	Go to Kaggle Account Settings
	Click "Create API Token" → it downloads kaggle.json.
	Place it in ~/.kaggle/kaggle.json.

4. Download The Dataset:
	kaggle datasets download -d <ashirwadsangwan/imdb-dataset> -p ./input --unzip

5. Run The Script:
	python main.py
