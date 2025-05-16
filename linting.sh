if ! command -v flake8 &> /dev/null
then
  pip install flake8
fi

flake8 --max-line-length=120 src

EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
  echo "Linting passed with no issues."
fi
