FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN pip3 install -r requirements.txt

# Copy code
COPY .env ${LAMBDA_TASK_ROOT}
COPY db.py ${LAMBDA_TASK_ROOT}
COPY model.py ${LAMBDA_TASK_ROOT}
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

