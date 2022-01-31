from typing import List, Tuple, Iterable
from piffle.presentation import IIIFPresentation
import random
import requests
import click
import shutil
import os
import tqdm

Uri = str
Filename = str
ImageList = List[Tuple[Uri, Filename]]


def get_images_from_manifest(url: Uri) -> ImageList:
    """ Gets a URI, read the manifest

    :param url: URI of a manifest
    :return: List of images link
    """
    return list([
        (canvas.images[0].resource.id, canvas.id.split("/")[-1]+".jpeg")
        for canvas in IIIFPresentation.from_url(url).sequences[0].canvases
    ])


def randomized(image_list: ImageList, number: int = 10) -> ImageList:
    """ Selects [number] images from ImageList

    :param image_list: List of images link and filename
    :param number: Number of images to select
    :return: Filtered image list
    """
    # In place randomization
    random.shuffle(image_list)
    return image_list[:max(number, len(image_list)-1)]


def save_images(images: ImageList, directory: str = "./") -> Iterable[str]:
    for url, filename in tqdm.tqdm(images):
        r = requests.get(url, stream=True, allow_redirects=True)
        if 200 <= r.status_code < 400:
            with open(os.path.join(directory, filename), 'wb') as f:
                r.raw.decode_content = True
                shutil.copyfileobj(r.raw, f)
                yield os.path.join(directory, filename)


@click.command()
@click.argument("manifest", type=click.STRING)
@click.option("directory", type=click.Path(exists=True, dir_okay=True, file_okay=False), default="./",
              help="Directory where to save the images")
@click.option("number", type=int, help="Number of images to save", default=10)
def cli(manifest, directory, number):
    """
    Example https://gallica.bnf.fr/iiif/ark:/12148/bpt6k12401693/manifest.json
    :return:
    """
    images = get_images_from_manifest(manifest)
    images = randomized(images, number=number)
    image_saved = save_images(images, directory=directory)
    for image in image_saved:
        click.echo(f"Saved {image}")


if __name__ == "__main__":
    # print(get_images_from_manifest("https://gallica.bnf.fr/iiif/ark:/12148/bpt6k12401693/manifest.json"))
    cli()
