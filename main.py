import typer
import os
import pathlib
from rich.console import Console
from rich.table import Table
from rich.tree import Tree
from rich.text import Text
from rich.filesize import decimal
from rich.markup import escape

app = typer.Typer(rich_markup_mode="rich")
console = Console()


@app.command(
    epilog="Made with :heart:  by [blue][link=https://github.com/Syntoxine]Syntoxine[/link][/blue]"
)
def main(
    directory: str = typer.Argument(
        ".\\",
        help="The directory which will be checked for duplicates.",
        show_default="Current directory",
    ),
    show_tree: bool = typer.Option(False, help="Show a tree of the working directory"),
) -> None:
    """Utility script to check for file duplicates."""
    if show_tree:

        def walk_directory(directory: pathlib.Path, tree: Tree) -> None:
            """
            Recursively builds a Tree with directory contents.
            Provided by Will McGugan
            """
            paths = sorted(
                pathlib.Path(directory).iterdir(),
                key=lambda path: (path.is_file(), path.name.lower()),
            )
            for path in paths:
                # Remove hidden files
                if path.name.startswith("."):
                    continue
                if path.is_dir():
                    style = "dim" if path.name.startswith("__") else ""
                    branch = tree.add(
                        f"[bold magenta]:open_file_folder: [link file://{path}]{escape(path.name)}",
                        style=style,
                        guide_style=style,
                    )
                    walk_directory(path, branch)
                else:
                    text_filename = Text(path.name, "green")
                    text_filename.highlight_regex(r"\..*$", "red")
                    text_filename.stylize(f"link file://{path}")
                    file_size = path.stat().st_size
                    text_filename.append(f" ({decimal(file_size)})", "blue")
                    match path.suffix:
                        case ".py": icon = "🐍 "
                        case ".png" | ".jpeg": icon = "🎨 "
                        case ".mov" | ".mp4": icon = "🎥 "
                        case _: icon = "📄 "
                    tree.add(Text(icon) + text_filename)
        
        fdirectory = os.path.abspath(directory)
        tree = Tree(
            f":open_file_folder: [link file://{fdirectory}]{fdirectory}",
            guide_style="bright_blue",
        )
        walk_directory(pathlib.Path(fdirectory), tree)
        console.print(tree)

    else:
        table = Table("Name", "Path", show_lines=True, title="Duplicates")

        file_paths = {}
        duplicates = []
        
        for root, dirs, files in os.walk(directory):
            for i in files:
                file_path = os.path.join(root, i)
                try:
                    file_paths[i] = [*file_paths[i],file_path]
                    duplicates.append(i)
                except KeyError:
                    file_paths[i] = [file_path]
            
            for i in duplicates:
                for j in file_paths[i]:
                    table.add_row(i, j)
            
        console.print(table)


if __name__ == "__main__":
    app()
