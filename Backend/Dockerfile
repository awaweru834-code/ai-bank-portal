# 1. The Foundation
FROM python:3.10-slim

# 2. Set the working directory
WORKDIR /code

# 3. Copy the shopping lists
COPY ./requirements.txt /code/requirements.txt

# 4. Install the packages
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# 5. Copy the rest of your code
COPY . /code/

# 6. Open the network port
EXPOSE 8000

# 7. The boot-up command
# 7. The boot-up command
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]