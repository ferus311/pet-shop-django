# python-naitei2024_pet-shop
Dự án shop e-com bán các sản phẩm dành cho thú cưng

# Setup
## tạo file môi trường .env
## Cài đặt các gói phụ thuộc
pip install -r requirements.txt
## migration
python3 manage.py migrate
## run
python3 manage.py runserver

## Kiểm thử format với pep8
pip install pycodestyle
pycodestyle .

## auto format code
pip install autopep8
autopep8 --in-place --aggressive --aggressive path/to/your/code.py
