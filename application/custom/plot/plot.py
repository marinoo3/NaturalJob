from .figures.cluster_fig import ClusterFig
from .figures.job_fig import JobFig
from .figures.contract_fig import ContractFig
from .figures.experience_fig import ExperienceFig




class Plot:

    def __init__(self):
        self.clusters = ClusterFig()
        self.job_fig = JobFig()
        self.contract_fig = ContractFig()
        self.experience_fig = ExperienceFig()