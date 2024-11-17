import argparse

import force_awakens.app as app
import force_awakens.web.server as web

from multiprocessing import Process, Queue


def main():
    # command line arguments
    parser = argparse.ArgumentParser(
        prog="The Force Awakens",
        description="2024 McGill Physics Hackathon, Dawson College",
    )

    # enable or disable web client connection capability
    parser.add_argument("-w", "--web", action="store_true")

    # webserver port
    parser.add_argument("-p", "--port", default=8080)

    # ngrok tunnel token,
    # create account on ngrok and feed authtoken here
    parser.add_argument("-t", "--token", default="")

    # optionally disable ngrok tunnel
    parser.add_argument("-n", "--no-tunnel", action="store_true")
    args = parser.parse_args()

    if args.web:
        # if web clients is enabled,
        # share a multiprocessing queue between
        # webserver and renderer, to sync acceleration
        # vector data between them
        vec_queue = Queue()

        # start webserver process in background
        web_proc = Process(
            target=web.server_process,
            args=(vec_queue, args.port),
            daemon=True,
        )
        web_proc.start()

        # create a public development link via ngrok
        # so that users can access webserver from public
        # QR code link

        import ngrok
        import qrcode

        if args.no_tunnel:
            url = f"http://127.0.0.1:{args.port}"
        else:
            # start ngrok tunnel for port, and expose webserver
            # to public QR code
            if args.token:
                listener = ngrok.connect(args.port, authtoken=args.token)
            else:
                listener = ngrok.connect(args.port, authtoken_from_env=True)
            url = listener.url()

        print(f"Ingress established at {url}")

        # generate QR code, and pass the image to 
        # the renderer
        img = qrcode.make(url)
        app.run(
            args.web,
            qr=img,
            vec_queue=vec_queue,
        )
    else:
        # run the app without web capabilities
        app.run(args.web)


if __name__ == "__main__":
    main()
