from sqlalchemy import *
from sqlalchemy.orm import joinedload, sessionmaker, declarative_base, Session
from sqlalchemy.exc import SQLAlchemyError
from typing import Generator, List, Dict, Any, Optional, Type
from contextlib import contextmanager
import logging

from db.connection import Connection

Base = declarative_base()


class MariaDB:
    """
    A wrapper class for SQLAlchemy with Mariadb database operations.

    Usage:
        db = MySQLDatabase(
            host='localhost',
            port=3306,
            user='root',
            password='password',
            database='mydb'
        )

        # Create tables
        db.create_tables()

        # Insert data
        db.insert(User(name='John', email='john@example.com'))

        # Query data
        users = db.query_all(User)
    """

    def __init__(
        self,
        con: Connection,
        database: str = "",
        pool_size: int = 5,
        max_overflow: int = 10,
        echo: bool = False,
    ):
        """
        Initialize MySQL database connection.

        Args:
            con: Connection object with host, port, username, password
            database: Database name
            pool_size: Connection pool size
            max_overflow: Maximum overflow connections
            echo: Enable SQL query logging
        """
        self.connection_string = (
            f"mysql+pymysql://{con.username}:{con.password}@{con.host}:{con.port}/{database}"
            "?charset=utf8mb4"
        )

        self.engine = create_engine(
            self.connection_string,
            pool_size=pool_size,
            max_overflow=max_overflow,
            echo=echo,
            pool_pre_ping=True,  # Verify connections before using
        )

        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

        self.metadata = MetaData()

        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """
        Context manager for database sessions.

        Yields:
            Session: SQLAlchemy session
        """
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            self.logger.error(f"Session error: {e}")
            raise
        finally:
            session.close()

    def create_tables(self, base: Type = Base) -> None:
        """
        Create all tables defined in the Base metadata.

        Args:
            base: Declarative base containing table definitions
        """
        try:
            base.metadata.create_all(bind=self.engine)
            self.logger.info("Tables created successfully")
        except SQLAlchemyError as e:
            self.logger.error(f"Error creating tables: {e}")
            raise

    def drop_tables(self, base: Type = Base) -> None:
        """
        Drop all tables defined in the Base metadata.

        Args:
            base: Declarative base containing table definitions
        """
        try:
            base.metadata.drop_all(bind=self.engine)
            self.logger.info("Tables dropped successfully")
        except SQLAlchemyError as e:
            self.logger.error(f"Error dropping tables: {e}")
            raise

    def insert(self, obj: Any) -> Any:
        """
        Insert a single object into the database.

        Args:
            obj: SQLAlchemy model instance

        Returns:
            The inserted object with updated attributes
        """
        with self.get_session() as session:
            session.add(obj)
            session.flush()
            session.refresh(obj)
            return obj

    def insert_many(self, objects: List[Any]) -> List[Any]:
        """
        Insert multiple objects into the database.

        Args:
            objects: List of SQLAlchemy model instances

        Returns:
            List of inserted objects
        """
        with self.get_session() as session:
            session.add_all(objects)
            session.flush()
            for obj in objects:
                session.refresh(obj)
            return objects

    def query_all(self, model: Type, limit: Optional[int] = None) -> List[Any]:
        """
        Query all records from a table.

        Args:
            model: SQLAlchemy model class
            limit: Optional limit on number of results

        Returns:
            List of model instances
        """
        with self.get_session() as session:
            query = session.query(model).options(joinedload())
            if limit:
                query = query.limit(limit)
            return query.all()

    @contextmanager
    def query_by_id(self, model: Type, id: Any) -> Generator[Optional[Any], None, None]:
        """
        Query a record by its primary key.

        Args:
            model: SQLAlchemy model class
            id: Primary key value

        Returns:
            Model instance or None
        """
        with self.get_session() as session:
            yield session.query(model).get(id)

    @contextmanager
    def query_filter(self, model: Type, **filters) -> Generator[List[Any], None, None]:
        """
        Query records with filters.

        Args:
            model: SQLAlchemy model class
            **filters: Keyword arguments for filtering

        Returns:
            List of model instances
        """
        with self.get_session() as session:
            yield session.query(model).filter_by(**filters).all()

    @contextmanager
    def query_first(
        self, model: Type, **filters
    ) -> Generator[Optional[Any], None, None]:
        """
        Query first record matching filters.

        Args:
            model: SQLAlchemy model class
            **filters: Keyword arguments for filtering

        Returns:
            Model instance or None
        """
        with self.get_session() as session:
            yield session.query(model).filter_by(**filters).first()

    @contextmanager
    def transaction(self) -> Generator[Session, None, None]:
        """
        Context manager for a transaction.

        Yields:
            Session: SQLAlchemy session
        """
        with self.get_session() as session:
            yield session

    def update(self, obj: Any) -> Any:
        """
        Update an existing object in the database.

        Args:
            obj: SQLAlchemy model instance with updated values

        Returns:
            Updated object
        """
        with self.get_session() as session:
            session.merge(obj)
            return obj

    def delete(self, obj: Any) -> None:
        """
        Delete an object from the database.

        Args:
            obj: SQLAlchemy model instance to delete
        """
        with self.get_session() as session:
            session.delete(obj)

    def delete_by_id(self, model: Type, id: Any) -> bool:
        """
        Delete a record by its primary key.

        Args:
            model: SQLAlchemy model class
            id: Primary key value

        Returns:
            True if deleted, False if not found
        """
        with self.get_session() as session:
            obj = session.query(model).get(id)
            if obj:
                session.delete(obj)
                return True
            return False

    def execute_raw(self, sql: str, params: Optional[Dict] = None) -> Any:
        """
        Execute raw SQL query.

        Args:
            sql: SQL query string
            params: Optional parameters for the query

        Returns:
            Query result
        """
        with self.get_session() as session:
            result = session.execute(text(sql), params or {})
            return result

    def count(self, model: Type, **filters) -> int:
        """
        Count records matching filters.

        Args:
            model: SQLAlchemy model class
            **filters: Keyword arguments for filtering

        Returns:
            Count of matching records
        """
        with self.get_session() as session:
            query = session.query(model)
            if filters:
                query = query.filter_by(**filters)
            return query.count()

    def close(self) -> None:
        """Close all database connections."""
        self.engine.dispose()
        self.logger.info("Database connections closed")
