import argparse
import sys


def runserver(args):
    import uvicorn

    uvicorn.run("wsgi-service:app", host=args.host, port=args.port)


def build(args):
    from app._set import RucCrawler

    ruc_crawler = RucCrawler()
    ruc_crawler.run()


def download(args):
    from app.utils import download
    from app.conf import settings

    if settings.RUC_DB_URL is None:
        print("RUC_DB_URL not found in environment variables")
    else:
        download(settings.RUC_DB_URL, "data/ruc.db")

    if settings.PEOPLE_DB_URL is None:
        print("PEOPLE_DB_URL not found in environment variables")
    else:
        download(settings.PEOPLE_DB_URL, "data/personas.db")


def main():
    parser = argparse.ArgumentParser(description="CLI for managing people")

    subparsers = parser.add_subparsers(title="commands", dest="command")
    subparsers.required = True

    # Command: runserver
    runserver_parser = subparsers.add_parser("runserver", help="Run the API server")
    runserver_parser.add_argument(
        "--port", type=int, default=3000, help="Specify the port to run the server on"
    )
    runserver_parser.add_argument(
        "--host",
        type=str,
        default="127.0.0.1",
        help="Specify the host address to run the server on",
    )
    runserver_parser.set_defaults(func=runserver)

    # Command: build
    build_parser = subparsers.add_parser(
        "build", help="Download the people data and build the database"
    )
    build_parser.set_defaults(func=build)

    # Command: download
    download_parser = subparsers.add_parser(
        "download", help="Download pre-built databases"
    )
    download_parser.set_defaults(func=download)

    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
