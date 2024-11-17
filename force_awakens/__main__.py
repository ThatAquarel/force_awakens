import argparse

import force_awakens.app as app
import force_awakens.web.server as web

from multiprocessing import Process, Queue


def main():
    parser = argparse.ArgumentParser(
        prog="The Force Awakens",
        description="2024 McGill Physics Hackathon, Dawson College",
    )

    parser.add_argument("-w", "--web", action="store_true")
    parser.add_argument("-p", "--port", default=8080)
    parser.add_argument("-t", "--token", default="")
    parser.add_argument("-n", "--no-tunnel", action="store_true")
    args = parser.parse_args()

    if args.web:
        vec_queue = Queue()

        web_proc = Process(
            target=web.server_process,
            args=(vec_queue,),
            daemon=True,
        )
        web_proc.start()

        import ngrok
        import qrcode

        if args.no_tunnel:
            url = "http://127.0.0.1:8080"
        else:
            if args.token:
                listener = ngrok.connect(args.port, authtoken=args.token)
            else:
                listener = ngrok.connect(args.port, authtoken_from_env=True)
            url = listener.url()

        print(f"Ingress established at {url}")

        img = qrcode.make(url)
        app.run(
            args.web,
            qr=img,
            vec_queue=vec_queue,
        )
    else:
        app.run(args.web)


if __name__ == "__main__":
    main()
