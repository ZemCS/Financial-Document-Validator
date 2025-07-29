# PDF Document Classifier API

A Flask-based REST API that classifies PDF documents as Bank Statements or Salary Slips using OCR, keyword matching, and metadata analysis.

## Features

- **Document Classification**: Automatically classifies PDFs as Bank Statements, Salary Slips, or Other
- **OCR Support**: Handles both text-based and scanned PDFs using Tesseract OCR
- **QR Code Detection**: Enhanced bank statement detection with QR code recognition
- **PDF Metadata Analysis**: Detects if PDFs have been modified after creation
- **Fuzzy String Matching**: Uses intelligent keyword matching with similarity scoring
- **RESTful API**: Simple HTTP endpoints for easy integration

## Installation

### Prerequisites

- Python 3.7+
- Tesseract OCR engine
- Poppler utilities (for PDF to image conversion)

### System Dependencies

#### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr poppler-utils
```

#### macOS
```bash
brew install tesseract poppler
```

#### Windows
- Download and install [Tesseract OCR](https://github.com/tesseract-ocr/tesseract)
- Download and install [Poppler for Windows](https://blog.alivate.com.au/poppler-windows/)

### Python Dependencies

```bash
pip install -r requirements.txt
```

Install the `requirements.txt` file

## Usage

### Starting the Server

```bash
python api.py
```

The API will be available at `http://localhost:5000`

### API Endpoints

#### 1. Bank Statement Classification

**Endpoint:** `POST /classify/bank-statement`

**Request:**
```bash
curl -X POST -F "file=@document.pdf" http://localhost:5000/classify/bank-statement
```

**Response:**
```json
{
  "classification": "Bank Statement",
  "match_count": 12,
  "scanned": false,
  "pdf_modified": true,
  "creation_date": "D:20240115120000",
  "modification_date": "D:20240115130000"
}
```

#### 2. Salary Slip Classification

**Endpoint:** `POST /classify/salary-slip`

**Request:**
```bash
curl -X POST -F "file=@payslip.pdf" http://localhost:5000/classify/salary-slip
```

**Response:**
```json
{
  "classification": "Salary Slip",
  "match_count": 8,
  "scanned": true,
  "pdf_modified": false,
  "creation_date": "D:20240115120000",
  "modification_date": "D:20240115120000"
}
```

## Configuration

### Thresholds

You can adjust classification thresholds in the code:

```python
THRESHOLD_BANK = 8    # Minimum matches for bank statement classification
THRESHOLD_SALARY = 7  # Minimum matches for salary slip classification
```

### Keywords

The system uses predefined keyword lists for classification:

**Bank Statement Keywords:**
- Statement of Account, Account Number, Debit, Credit, IBAN, etc.

**Salary Slip Keywords:**
- Wages, Pay Slip, Basic Salary, Allowances, Net Amount, etc.

## How It Works

1. **File Upload**: PDF files are uploaded via HTTP POST requests
2. **Text Extraction**: 
   - For text-based PDFs: Direct text extraction using PyPDF2
   - For scanned PDFs: OCR processing using Tesseract
3. **Keyword Matching**: Fuzzy string matching against predefined keyword lists
4. **QR Code Detection**: Additional scoring for bank statements with QR codes
5. **Metadata Analysis**: Checks PDF creation and modification dates
6. **Classification**: Documents are classified based on match count thresholds

## Response Fields

| Field | Description |
|-------|-------------|
| `classification` | Document type: "Bank Statement", "Salary Slip", or "Other" |
| `match_count` | Number of keywords matched in the document |
| `scanned` | Boolean indicating if the PDF was scanned (image-based) |
| `pdf_modified` | Boolean indicating if the PDF was modified after creation |
| `creation_date` | PDF creation timestamp |
| `modification_date` | PDF last modification timestamp |

## Error Handling

The API returns appropriate HTTP status codes:

- `200 OK`: Successful classification
- `400 Bad Request`: No file uploaded or invalid request
- `500 Internal Server Error`: Processing errors

## Security Considerations

- Temporary files are automatically cleaned up after processing
- File uploads are processed in a sandboxed manner
- Consider implementing file size limits and validation in production

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/new-feature`)
3. Commit your changes (`git commit -am 'Add new feature'`)
4. Push to the branch (`git push origin feature/new-feature`)
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Troubleshooting

### Common Issues

1. **Tesseract not found**: Ensure Tesseract is installed and in your system PATH
2. **Poppler utilities missing**: Install poppler-utils for PDF to image conversion
3. **Memory issues with large PDFs**: Consider implementing file size limits
4. **OCR accuracy**: Preprocessing images can improve OCR results

### Performance Tips

- For production use, consider implementing caching mechanisms
- Use a proper WSGI server like Gunicorn instead of Flask's development server
- Implement async processing for large files

## Support

For issues and questions, please open an issue on GitHub or contact the maintainers.
