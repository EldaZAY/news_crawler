import csv
from collections import defaultdict
import http.client
import sys


def generate_report(sitename):
    fetches_attempted = 0
    fetches_succeeded = 0
    total_urls_extracted = 0
    unique_urls = set()
    status_codes = defaultdict(int)
    file_sizes = defaultdict(int)
    content_types = defaultdict(int)

    # Process fetch CSV
    with open(f'fetch_{sitename}.csv', 'r') as fetch_file:
        fetch_reader = csv.reader(fetch_file)
        next(fetch_reader)  # Skip header
        for row in fetch_reader:
            fetches_attempted += 1
            status = int(row[1])
            status_codes[status] += 1
            if 200 <= status < 300:
                fetches_succeeded += 1

    # Process visit CSV
    with open(f'visit_{sitename}.csv', 'r') as visit_file:
        visit_reader = csv.reader(visit_file)
        next(visit_reader)  # Skip header
        for row in visit_reader:
            size = int(row[1])
            content_type = row[3]
            content_types[content_type] += 1
            if size < 1024:
                file_sizes['< 1KB'] += 1
            elif size < 10 * 1024:
                file_sizes['1KB ~ <10KB'] += 1
            elif size < 100 * 1024:
                file_sizes['10KB ~ <100KB'] += 1
            elif size < 1024 * 1024:
                file_sizes['100KB ~ <1MB'] += 1
            else:
                file_sizes['>= 1MB'] += 1

    # Process URLs CSV
    with open(f'urls_{sitename}.csv', 'r') as urls_file:
        urls_reader = csv.reader(urls_file)
        next(urls_reader)  # Skip header
        for row in urls_reader:
            total_urls_extracted += 1
            unique_urls.add((row[0], row[1]))

    # Generate report
    with open(f'crawl_report_{sitename}.txt', 'w') as report:
        report.write("Name: Aiyu Zhang\n")
        report.write("USC ID: 8524183902\n")
        report.write(f"News site crawled: {sitename}.com\n")
        report.write(f"Number of threads: 6\n\n")

        report.write("Fetch Statistics\n")
        report.write("================\n")
        report.write(f"# fetches attempted: {fetches_attempted}\n")
        report.write(f"# fetches succeeded: {fetches_succeeded}\n")
        report.write(f"# fetches failed or aborted: {fetches_attempted - fetches_succeeded}\n\n")

        report.write("Outgoing URLs:\n")
        report.write("==============\n")
        n_unique_urls = len(unique_urls)
        n_unique_urls_OK = sum(1 for _, indicator in unique_urls if indicator == 'OK')
        report.write(f"Total URLs extracted: {total_urls_extracted}\n")
        report.write(f"# unique URLs extracted: {n_unique_urls}\n")
        report.write(f"# unique URLs within News Site: {n_unique_urls_OK}\n")
        report.write(f"# unique URLs outside News Site: {n_unique_urls - n_unique_urls_OK}\n\n")

        report.write("Status Codes:\n")
        report.write("=============\n")
        for status, count in sorted(status_codes.items()):
            status_string = http.client.responses.get(status, 'Unknown')
            report.write(f"{status} {status_string}: {count}\n")
        report.write("\n")

        report.write("File Sizes:\n")
        report.write("===========\n")
        for size_range, count in file_sizes.items():
            report.write(f"{size_range}: {count}\n")
        report.write("\n")

        report.write("Content Types:\n")
        report.write("==============\n")
        for content_type, count in content_types.items():
            report.write(f"{content_type}: {count}\n")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python report.py <sitename>")
        sys.exit(1)

    sitename = sys.argv[1]
    generate_report(sitename)
    print(f"Report generated: crawl_report_{sitename}.txt")