from .figures.cluster_fig import ClusterFig
from .figures.job_fig import JobFig
from .figures.contract_fig import ContractFig




class Plot:

    def __init__(self):
        self.clusters = ClusterFig()
        self.job_fig = JobFig()
        self.contract_fig = ContractFig()