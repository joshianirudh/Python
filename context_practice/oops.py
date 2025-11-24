"""
Practice file: Python OOP (classes, abstract methods, classmethods, staticmethods, dataclasses)

INSTRUCTIONS
------------
1. Read through the code and follow each TODO.
2. Implement:
   - Task.from_dict (classmethod)
   - Task.validate_priority (staticmethod)
   - InMemoryTaskRepository internals and methods
   - InMemoryTaskRepository.from_tasks (classmethod)
   - TaskService.create_task (instance method)

3. Run the tests:
   - Either: `python this_file.py`
   - Or:     `pytest this_file.py` (pytest will detect unittest tests)

4. All tests should PASS when you're done.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Dict, List


# =========================
# Domain model
# =========================

@dataclass
class Task:
    """
    Simple value object representing a Task.

    Fields:
        id:       unique integer identifier
        title:    short description
        is_done:  True if completed
        priority: integer 1–5 (1 = lowest, 5 = highest)
    """
    id: int
    title: str
    is_done: bool = False
    priority: int = 1

    # TODO: implement this classmethod
    # Requirements:
    #   - Accepts a dict with keys:
    #       "id" (required),
    #       "title" (required),
    #       "is_done" (optional, default False),
    #       "priority" (optional, default 1)
    #   - Returns a Task instance.
    #   - Should NOT mutate the input dict.
    @classmethod
    def from_dict(cls, data: dict) -> "Task":
        id, title, is_done, priority = data['id'], data['title'], data.get('is_done', False), data.get('priority', 1)
        return cls(id, title, is_done, priority)

    # TODO: implement this staticmethod
    # Requirements:
    #   - Return True if priority is an int between 1 and 5 (inclusive)
    #   - Return False otherwise
    @staticmethod
    def validate_priority(priority: int) -> bool:
        return priority >= 1 and priority <= 5


# =========================
# Repository abstraction
# =========================

class TaskRepository(ABC):
    """Abstract base class for task storage."""

    @abstractmethod
    def add(self, task: Task) -> None:
        """
        Store a new task.
        Must:
          - Raise ValueError if a task with the same id already exists.
        """
        raise NotImplementedError

    @abstractmethod
    def get(self, task_id: int) -> Task:
        """
        Return the task with the given id.
        Must:
          - Raise KeyError if the task does not exist.
        """
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> List[Task]:
        """
        Return a list of ALL tasks (done and not done).
        Order does not matter.
        """
        raise NotImplementedError

    @abstractmethod
    def list_open_tasks(self) -> List[Task]:
        """
        Return a list of tasks where is_done is False.
        Order does not matter.
        """
        raise NotImplementedError

    @abstractmethod
    def mark_done(self, task_id: int) -> None:
        """
        Mark the task with the given id as done.
        Must:
          - Raise KeyError if the task does not exist.
        """
        raise NotImplementedError


# =========================
# Concrete implementation
# =========================

class InMemoryTaskRepository(TaskRepository):
    """
    In-memory implementation of TaskRepository using a dict.
    Keys:   task id (int)
    Values: Task instances
    """

    def __init__(self) -> None:
        # TODO:
        #   - Initialize an internal dict[int, Task] to store the tasks.
        #     A typical name would be self._tasks.
        self._tasks = {}

    # TODO: implement all abstract methods using the internal dict.

    def add(self, task: Task) -> None:
        # Requirements:
        #   - If task.id already exists in the dict, raise ValueError
        #   - Otherwise, store it.
        if task.id in self._tasks:
            raise ValueError(f"Task id: {task.id} already exists!")
        
        self._tasks[task.id] = task

    def get(self, task_id: int) -> Task:
        # Requirements:
        #   - Return the task with this id
        #   - Raise KeyError if not found
        if task_id in self._tasks:
            return self._tasks[task_id]
        raise KeyError(f"Key: {task_id} not found!")

    def list_all(self) -> List[Task]:
        # Requirements:
        #   - Return a list of all tasks stored.
        results = []
        for _, val in self._tasks.items():
            results.append(val)
        
        return results

    def list_open_tasks(self) -> List[Task]:
        # Requirements:
        #   - Return only tasks where is_done is False.
        results = []
        for _, val in self._tasks.items():
            if not val.is_done:
                results.append(val)
        
        return results

    def mark_done(self, task_id: int) -> None:
        # Requirements:
        #   - Set is_done=True for the task with this id.
        #   - Raise KeyError if not found.
        if self._tasks[task_id]:
            self._tasks[task_id].is_done = True
        else:
            raise KeyError(f"Key: {task_id} not found!")

    # TODO: implement this classmethod
    # Requirements:
    #   - Create a new InMemoryTaskRepository.
    #   - Add all given tasks to it using self.add (so duplicate ids still raise).
    #   - Return the repository instance.
    @classmethod
    def from_tasks(cls, tasks: List[Task]) -> "InMemoryTaskRepository":
        obj = cls()
        for task in tasks:
            obj.add(task)
        return obj


# =========================
# Service layer
# =========================

class TaskService:
    """
    High-level API for working with tasks.

    This is intentionally simple, but it shows how you'd layer
    application logic on top of a repository interface.
    """

    def __init__(self, repo: TaskRepository, starting_id: int = 1) -> None:
        self._repo = repo
        self._next_id = starting_id

    # TODO: implement this instance method
    # Requirements:
    #   - Validate priority using Task.validate_priority.
    #       - If invalid, raise ValueError.
    #   - Create a new Task with:
    #       id       = current self._next_id
    #       title    = title argument
    #       is_done  = False
    #       priority = priority argument
    #   - Add the task to the repository.
    #   - Increment self._next_id by 1.
    #   - Return the created Task.
    def create_task(self, title: str, priority: int = 1) -> Task:
        if not Task(self._next_id, title).validate_priority(priority):
            raise ValueError(f"Task priority: {priority} not between 1 & 5 (inclusive)")
        task = Task(id=self._next_id, title=title, is_done=False, priority=priority)
        self._repo.add(task)
        self._next_id += 1
        return task

    def complete_task(self, task_id: int) -> None:
        """
        Convenience wrapper that just delegates to the repo.
        You do NOT need to modify this method, but you can inspect it.
        """
        self._repo.mark_done(task_id)

    def list_open_tasks(self) -> List[Task]:
        """Again, just delegating to the repository."""
        return self._repo.list_open_tasks()


# =========================
# Tests
# =========================

import unittest


class TaskModelTests(unittest.TestCase):
    def test_from_dict_uses_defaults(self):
        data = {
            "id": 10,
            "title": "Write docs",
            # "is_done" and "priority" omitted on purpose
        }
        task = Task.from_dict(data)
        self.assertEqual(task.id, 10)
        self.assertEqual(task.title, "Write docs")
        self.assertFalse(task.is_done)
        self.assertEqual(task.priority, 1)

    def test_from_dict_overrides_defaults(self):
        data = {
            "id": 20,
            "title": "Fix bug",
            "is_done": True,
            "priority": 5,
        }
        task = Task.from_dict(data)
        self.assertEqual(task.id, 20)
        self.assertEqual(task.title, "Fix bug")
        self.assertTrue(task.is_done)
        self.assertEqual(task.priority, 5)

    def test_validate_priority(self):
        self.assertTrue(Task.validate_priority(1))
        self.assertTrue(Task.validate_priority(3))
        self.assertTrue(Task.validate_priority(5))
        self.assertFalse(Task.validate_priority(0))
        self.assertFalse(Task.validate_priority(6))
        self.assertFalse(Task.validate_priority(-1))


class InMemoryTaskRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.repo = InMemoryTaskRepository()

    def test_add_and_get(self):
        t1 = Task(id=1, title="A")
        self.repo.add(t1)
        fetched = self.repo.get(1)
        self.assertIs(fetched, t1)

    def test_add_duplicate_raises_value_error(self):
        t1 = Task(id=1, title="A")
        t2 = Task(id=1, title="B")
        self.repo.add(t1)
        with self.assertRaises(ValueError):
            self.repo.add(t2)

    def test_get_missing_raises_key_error(self):
        with self.assertRaises(KeyError):
            self.repo.get(999)

    def test_list_all_and_open_tasks(self):
        t1 = Task(id=1, title="Open 1", is_done=False)
        t2 = Task(id=2, title="Open 2", is_done=False)
        t3 = Task(id=3, title="Done", is_done=True)
        self.repo.add(t1)
        self.repo.add(t2)
        self.repo.add(t3)

        all_tasks = self.repo.list_all()
        self.assertCountEqual(all_tasks, [t1, t2, t3])

        open_tasks = self.repo.list_open_tasks()
        self.assertCountEqual(open_tasks, [t1, t2])

    def test_mark_done(self):
        t1 = Task(id=1, title="To be completed")
        self.repo.add(t1)
        self.repo.mark_done(1)
        self.assertTrue(self.repo.get(1).is_done)

        # Once done, it should no longer appear in open tasks
        open_tasks = self.repo.list_open_tasks()
        self.assertEqual(open_tasks, [])

    def test_mark_done_missing_raises_key_error(self):
        with self.assertRaises(KeyError):
            self.repo.mark_done(123)

    def test_from_tasks_classmethod(self):
        t1 = Task(id=1, title="A")
        t2 = Task(id=2, title="B", is_done=True)
        repo = InMemoryTaskRepository.from_tasks([t1, t2])

        all_tasks = repo.list_all()
        self.assertCountEqual(all_tasks, [t1, t2])


class TaskServiceTests(unittest.TestCase):
    def setUp(self):
        self.repo = InMemoryTaskRepository()
        self.service = TaskService(self.repo, starting_id=100)

    def test_create_task_assigns_ids_and_stores(self):
        task1 = self.service.create_task("First task", priority=2)
        task2 = self.service.create_task("Second task", priority=3)

        self.assertEqual(task1.id, 100)
        self.assertEqual(task2.id, 101)

        # Should be stored in the repo
        self.assertIs(self.repo.get(100), task1)
        self.assertIs(self.repo.get(101), task2)

    def test_create_task_validates_priority(self):
        # valid
        t = self.service.create_task("OK priority", priority=1)
        self.assertEqual(t.priority, 1)

        # invalid -> ValueError
        with self.assertRaises(ValueError):
            self.service.create_task("Bad priority", priority=10)

    def test_complete_task_flows_through_to_repo(self):
        task = self.service.create_task("To be completed", priority=2)
        self.service.complete_task(task.id)
        fetched = self.repo.get(task.id)
        self.assertTrue(fetched.is_done)

    def test_list_open_tasks(self):
        t1 = self.service.create_task("task 1", priority=1)
        t2 = self.service.create_task("task 2", priority=2)
        self.service.complete_task(t1.id)

        open_tasks = self.service.list_open_tasks()
        self.assertEqual(open_tasks, [t2])


if __name__ == "__main__":
    unittest.main()
