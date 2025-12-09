import sys
import dns.resolver
import smtplib
import os
import socket

def verify_email_smtp(email, from_address='test@example.com', timeout=20):
    """
    Attempts to verify the existence of an email address via SMTP.
    Returns True if the server *appears* to accept the address, False otherwise.
    This is not 100% reliable, as many servers deliberately mask whether an address exists.
    """
    try:
        local_part, domain = email.split('@')
    except ValueError:
        # If the email doesn't have exactly one '@', it's malformed
        return False

    # Try to get MX records for the domain
    try:
        answers = dns.resolver.resolve(domain, 'MX')
        # Sort by lowest preference
        mx_hosts = [str(r.exchange).strip('.') for r in sorted(answers, key=lambda r: r.preference)]
    except (dns.resolver.NoAnswer, dns.resolver.NXDOMAIN):
        # No MX record found, try to see if there's an A record for the domain
        try:
            dns.resolver.resolve(domain, 'A')
            # If domain has an A record, let's try connecting to it as a fallback
            mx_hosts = [domain]
        except:
            # No A record either -> domain likely doesn't exist
            return False
    except Exception:
        # Some other DNS error
        return False

    # Try each MX server until one connects successfully
    for mx in mx_hosts:
        try:
            with smtplib.SMTP(mx, 25, timeout=timeout) as server:
                server.ehlo_or_helo_if_needed()

                # Optional: some servers require TLS to proceed
                # You can try enabling TLS if you wish:
                # server.starttls()
                # server.ehlo_or_helo_if_needed()

                code, resp = server.mail(from_address)
                if code not in (250, 251):
                    # The server didn't like our MAIL FROM
                    continue

                code, resp = server.rcpt(email)

                # 250 or 251 means "we'll accept it". 550/551 typically means "nope".
                # 450/451/452 might be a temporary failure (greylisting).
                # But for simplicity, let's treat 250/251 as "valid"
                if code in (250, 251):
                    return True
                else:
                    # Possibly a 450/451 meaning "try again later" - can cause false negatives
                    # If you'd like to reduce false negatives, you could re-try or treat
                    # certain 4xx codes as "maybe valid". For now we treat them as invalid.
                    pass
        except (smtplib.SMTPConnectError, smtplib.SMTPServerDisconnected, socket.timeout) as e:
            # Connection problems; try next MX
            continue
        except Exception:
            # Any other error; let's just continue with next MX
            continue

    return False


if __name__ == "__main__":
    input_file = sys.argv[1]
    output_file = sys.argv[2]

    with open(input_file, 'r') as f:
        emails = [e.strip() for e in f if e.strip()]

    # Figure out where we left off (if output_file already exists)
    last_valid_email = None
    if os.path.exists(output_file):
        with open(output_file, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
            if lines:
                last_valid_email = lines[-1]

    start_index = emails.index(last_valid_email) + 1 if last_valid_email in emails else 0
    emails_to_check = emails[start_index:]

    for i, email in enumerate(emails_to_check, start=1):
        print(f"{i}/{len(emails_to_check)} Checking: {email}")

        try:
            result = verify_email_smtp(email)
            if result:
                print(f"{email} -> valid")
                with open(output_file, 'a') as f:
                    f.write(email + '\n')
            else:
                print(f"{email} -> invalid or uncertain")
        except Exception as e:
            # Catch-all so a single failure doesn't kill the loop
            print(f"Error verifying {email}: {e}")
    
