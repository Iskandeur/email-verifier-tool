# Email Question Mark

This is a command-line Python tool to check if email addresses from a file exist by querying their respective mail servers.

## Features

- Reads a list of email addresses from a text file.
- For each email, it checks the corresponding MX records and attempts SMTP verification.
- Generates an output file with one email and its verification status (`valid` or `invalid`) per line.
- Displays progress in the console to track the verification process for large lists.

## Requirements

- Python 3.x
- `dns.resolver` (Install via `pip install dnspython`)
- Internet connection (to resolve DNS queries and connect to mail servers)
  
Please note that some mail servers may not allow or respond correctly to SMTP `RCPT` commands, which can lead to false negatives. Also, some servers might employ spam detection measures that affect the verification process.

## Usage

1. Install the dependencies:
   ```bash
   pip install dnspython
   ```

2. Create an input file (e.g., `emails.txt`) with one email address per line:
   ```
   test@example.com
   hello@domain.com
   user@anotherdomain.net
   ```

3. Run the script:
   ```bash
   python verify_emails.py emails.txt results.txt
   ```

4. The console will display the progress as it processes each email:
   ```
   1/3 test@example.com
   2/3 hello@domain.com
   3/3 user@anotherdomain.net
   ```

5. Once complete, the `results.txt` file will contain the verification status:
   ```
   test@example.com valid
   hello@domain.com invalid
   user@anotherdomain.net invalid
   ```

## Disclaimer

This script attempts to verify email existence based on MX records and SMTP responses. It does not send actual emails, but it still connects to mail servers, which may cause security or reputation concerns when done frequently or in large volumes. Use this tool responsibly and in compliance with applicable laws and regulations.
