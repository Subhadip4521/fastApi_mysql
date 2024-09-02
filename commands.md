pip install fastapi
pip install uvicorn
pip install pymysql
pip install sqlalchemy

pip install python-decouple
pip install python-jose
pip install passlib
pip install bcrypt

python -m venv myenv
.\myenv\Scripts\Activate

uvicorn index:app --reload
