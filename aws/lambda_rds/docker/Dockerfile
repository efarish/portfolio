FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

# Copy requirements.txt
COPY requirements.txt ${LAMBDA_TASK_ROOT}

# Install the specified packages
RUN pip3 install -r requirements.txt

# Copy code
COPY .env ${LAMBDA_TASK_ROOT}
COPY *.py ${LAMBDA_TASK_ROOT}
RUN mkdir /${LAMBDA_TASK_ROOT}/entity
COPY ./entity/*.py /${LAMBDA_TASK_ROOT}/entity


