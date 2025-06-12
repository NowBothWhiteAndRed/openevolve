"""
Tests for ProgramDatabase in openevolve.database
"""

import unittest
from openevolve.config import Config
from openevolve.database import Program, ProgramDatabase


class TestProgramDatabase(unittest.TestCase):
    """Tests for program database"""

    def setUp(self):
        """Set up test database"""
        config = Config()
        config.database.in_memory = True
        self.db = ProgramDatabase(config.database)

    def test_add_and_get(self):
        """Test adding and retrieving a program"""
        program = Program(
            id="test1",
            code="def test(): pass",
            language="python",
            metrics={"score": 0.5},
        )

        self.db.add(program)

        retrieved = self.db.get("test1")
        self.assertIsNotNone(retrieved)
        self.assertEqual(retrieved.id, "test1")
        self.assertEqual(retrieved.code, "def test(): pass")
        self.assertEqual(retrieved.metrics["score"], 0.5)

    def test_get_best_program(self):
        """Test getting the best program"""
        program1 = Program(
            id="test1",
            code="def test1(): pass",
            language="python",
            metrics={"score": 0.5},
        )

        program2 = Program(
            id="test2",
            code="def test2(): pass",
            language="python",
            metrics={"score": 0.7},
        )

        self.db.add(program1)
        self.db.add(program2)

        best = self.db.get_best_program()
        self.assertIsNotNone(best)
        self.assertEqual(best.id, "test2")

    def test_sample(self):
        """Test sampling from the database"""
        program1 = Program(
            id="test1",
            code="def test1(): pass",
            language="python",
            metrics={"score": 0.5},
        )

        program2 = Program(
            id="test2",
            code="def test2(): pass",
            language="python",
            metrics={"score": 0.7},
        )

        self.db.add(program1)
        self.db.add(program2)

        parent, inspirations = self.db.sample()

        self.assertIsNotNone(parent)
        self.assertIn(parent.id, ["test1", "test2"])

    def test_island_inspiration_ratio(self):
        """Inspirations can be forced to come from the current island"""
        config = Config()
        config.database.in_memory = True
        config.database.num_islands = 2
        config.database.exploration_ratio = 1.0
        config.database.island_inspiration_ratio = 1.0
        db = ProgramDatabase(config.database)

        p1 = Program(id="p1", code="a", metrics={"score": 0.1})
        p2 = Program(id="p2", code="b", metrics={"score": 0.2})
        db.add(p1, target_island=0)
        db.add(p2, target_island=0)

        p3 = Program(id="p3", code="c", metrics={"score": 0.3})
        db.add(p3, target_island=1)

        db.set_current_island(0)
        parent, inspirations = db.sample()

        self.assertTrue(all(prog.metadata.get("island") == 0 for prog in inspirations))
        self.assertEqual(len(inspirations), 2)


if __name__ == "__main__":
    unittest.main()
