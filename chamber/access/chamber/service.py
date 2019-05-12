"""Module encapsulates access to experimental data."""

from sqlalchemy import create_engine, and_
from sqlalchemy.orm import sessionmaker

from chamber.access.chamber.models import Base, Experiment, Pool, Setting
from chamber.ifx.configuration import get_value


class ExperimentalAccess(object):
    """
    Encapsulates all aspects of data access for an experiment.

    Attributes
    ----------
    engine : sqlalchemy.engine.base.Engine
        The engine used to create sessions with the database.

    """

    def __init__(self):
        """Create the SQLAlchemy engine for the MySQL database."""
        # Get server configuration
        host = get_value('host', 'MySQL-Server')
        user = get_value('user', 'MySQL-Server')
        password = get_value('password', 'MySQL-Server')

        # Create engine
        conn_string = f'mysql+mysqlconnector://{user}:{password}@{host}/'
        self._engine = create_engine(conn_string, echo=False)

        # Create the schema if it doesn't exist
        self._schema = 'experimental'
        self._engine.execute(
            f'CREATE DATABASE IF NOT EXISTS `{self._schema}`;')

        # Create tables if they don't exist
        Base.metadata.create_all(self._engine)

        # Session factory
        self.Session = sessionmaker(bind=self._engine)

    def teardown(self):
        """
        Completely teardown database.

        This drops all of the tables, delets the databse, and disposes of the
        objects engine.

        """
        # Drop all tables
        Base.metadata.drop_all(self._engine)
        # Remove the schema
        self._engine.execute(f'DROP DATABASE IF EXISTS `experimental`;')
        # Dispose of the engine
        self._engine.dispose()

    def add_pool(self, pool_spec):
        """
        Add a pool to the database and return its primary key.

        If the pool already exists in the database, no new pool is added and
        the primary key for the existing pool is returned.

        Parameters
        ----------
        pool_spec : chamber.access.chamber.models.PoolSpec
            Specification for the pool to be added.

        Returns
        -------
        int
            Primary key for the pool that was added.

        """
        session = self.Session()

        try:
            # Check if pool exists
            query = session.query(Pool.pool_id).filter(
                and_(
                    Pool.inner_diameter == pool_spec.inner_diameter,
                    Pool.outer_diameter == pool_spec.outer_diameter,
                    Pool.height == pool_spec.height,
                    Pool.material == pool_spec.material,
                    Pool.mass == pool_spec.mass
                    )
                )
            pool_id = query.first()
            # If not, insert it
            if not pool_id:
                pool_to_add = Pool(
                    inner_diameter=pool_spec.inner_diameter,
                    outer_diameter=pool_spec.outer_diameter,
                    height=pool_spec.height,
                    material=pool_spec.material,
                    mass=pool_spec.mass)
                session.add(pool_to_add)
                session.commit()
                return pool_to_add.pool_id
            else:
                return pool_id[0]
        except:
            session.rollback()
        finally:
            session.close()

    def add_setting(self, setting_spec):
        """
        Add a setting to the database and return its primary key.

        If the setting already exists in the database, no new setting is added
        and the primary key for the existing setting is returned.

        Parameters
        ----------
        setting_spec : chamber.access.chamber.models.SettingSpec
            Specification for the setting to be added.

        Returns
        -------
        int
            Primary key for the setting that was added.

        """
        session = self.Session()

        try:
            # Check if the setting exists
            query = session.query(Setting.setting_id).filter(
                and_(
                    Setting.duty == setting_spec.duty,
                    Setting.pressure == setting_spec.pressure,
                    Setting.temperature == setting_spec.temperature,
                    Setting.time_step == setting_spec.time_step
                    )
                )
            setting_id = query.first()
            # If not, insert it
            if not setting_id:
                setting_to_add = Setting(
                    duty=setting_spec.duty,
                    pressure=setting_spec.pressure,
                    temperature=setting_spec.temperature,
                    time_step=setting_spec.time_step)
                session.add(setting_to_add)
                session.commit()
                return setting_to_add.setting_id
            else:
                return setting_id[0]
        except:
            session.rollback()
        finally:
            session.close()

    def add_experiment(self, experiment_spec):
        """
        Add an experiment to the database and return its primary key.

        If the experiment already exists in the database, no new experiment is
        added and the primary key for the existing experiment is returned.

        Parameters
        ----------
        experiment_spec : chamber.access.chamber.models.ExperimentSpec
            Specification for the experiment to be added.

        Returns
        -------
        int
            Primary key for the experiment that was added.

        """
        session = self.Session()

        try:
            # Check if the experiment exists
            query = session.query(Experiment.experiment_id)
            query = query.filter(Experiment.datetime == experiment_spec.datetime)
            experiment_id = query.first()
            # If not, insert it
            if not experiment_id:
                experiment_to_add = Experiment(
                    author=experiment_spec.author,
                    datetime=experiment_spec.datetime,
                    description=experiment_spec.description,
                    pool_id=experiment_spec.pool_id,
                    setting_id=experiment_spec.setting_id)
                session.add(experiment_to_add)
                session.commit()
                return experiment_to_add.experiment_id
            else:
                return experiment_id[0]
        except:
            session.rollback()
        finally:
            session.close()
