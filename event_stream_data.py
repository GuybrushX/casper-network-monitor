from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, DateTime, Boolean

Base = declarative_base()


class Deploy(Base):
    __tablename__ = "deploy"

    deploy_hash = Column(String(length=64), primary_key=True)
    account = Column(String(length=80))
    block_hash = Column(String(length=64))
    timestamp = Column(DateTime)
    ttl_secs = Column(Integer)
    cost = Column(Integer)


class Transfer(Base):
    __tablename__ = "transfer"

    deploy_hash = Column(String(length=64), primary_key=True)
    account = Column(String(length=80))
    block_hash = Column(String(length=64))
    timestamp = Column(DateTime)
    ttl_secs = Column(Integer)
    cost = Column(Integer)


class Block(Base):
    __tablename__ = "block"

    block_hash = Column(String(length=64), primary_key=True)
    state_root_hash = Column(String(length=64))
    body_hash = Column(String(length=64))
    accumulated_seed = Column(String)
    era_end_id = Column(Integer, nullable=True)
    era_id = Column(Integer)
    height = Column(Integer)
    proposer = Column(String)


class BlockDeploy(Base):
    __tablename__ = "block_deploy"

    block_hash = Column(String(length=64))
    deploy_hash = Column(String(length=64))


class BlockTransfer(Base):
    __tablename__ = "block_transfer"

    block_hash = Column(String(length=64))
    deploy_hash = Column(String(length=64))


class FinalitySignature(Base):
    __tablename__ = "finality_signature"

    id = Column(Integer, primary_key=True)
    block_hash = Column(String(length=64))
    era_id = Column(Integer)
    signature = Column(String)
    public_key = Column(String)
