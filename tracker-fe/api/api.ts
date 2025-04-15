import axios from 'axios';
import { Job, Candidate } from '../types/types';

const api = axios.create({
    baseURL: 'http://0.0.0.0:8000',
});

export const getJobs = async (): Promise<Job[]> => {
    const response = await api.get('/jobs');
    return response.data as Job[];
};

export const getCandidates = async (jobId: string): Promise<Candidate[]> => {
    const response = await api.get('/candidates', { params: { job_id: jobId } });
    return response.data as Candidate[];
};