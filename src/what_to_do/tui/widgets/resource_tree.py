from uuid import UUID

from textual.app import ComposeResult
from textual.events import Mount
from textual.widgets import Static, Tree

from what_to_do.client.group_clients import GroupClient
from what_to_do.client.project_clients import ProjectClient
from what_to_do.tasks.models import ResourceType
from what_to_do.tui.helpers import get_tui_client


class ResourceTreePanel(Static):
    """Display the Groups and Projects"""

    def __init__(self) -> None:
        super().__init__()

        # Configure Tree widget (builtin from Textual)
        self.resource_tree: Tree[tuple[ResourceType, UUID]] = Tree(
            "", id="resource-tree"
        )
        self.resource_tree.show_root = False

        # display when no groups are available
        self.empty_tree_message = Static("No groups available. Hence, no tasks yet.")

    def compose(self) -> ComposeResult:
        yield self.empty_tree_message
        yield self.resource_tree

    def _on_mount(self, event: Mount) -> None:
        super()._on_mount(event)
        self.add_nodes()

    def add_nodes(self) -> None:
        """Populate the tree view"""

        with get_tui_client(ResourceType.GROUPS) as client:
            assert isinstance(client, GroupClient)

            # outer level: groups
            groups = client.get_all()
            if not groups:
                self.empty_tree_message.display = True
                self.resource_tree.display = False
                return

            self.empty_tree_message.display = False
            self.resource_tree.display = True

            for group in client.get_all():
                group_node = self.resource_tree.root.add(
                    label=group.name,
                    data=(ResourceType.GROUPS, group.id),
                )

                # show projects below group
                for project in client.list_projects(group.id):
                    project_node = group_node.add(
                        label=project.name,
                        data=(ResourceType.PROJECTS, project.id),
                    )

                    # TODO --> Maybe remove this part once middle panel is implemented
                    with get_tui_client(ResourceType.PROJECTS) as proj_client:
                        assert isinstance(proj_client, ProjectClient)
                        for task in proj_client.list_tasks(project.id):
                            project_node.add_leaf(
                                label=task.title, data=(ResourceType.TASKS, task.id)
                            )

                # show remaining tasks (assigned to only a group)
                for task in client.list_tasks(group.id):
                    if task.project_id is None:
                        group_node.add_leaf(
                            label=task.title, data=(ResourceType.TASKS, task.id)
                        )
