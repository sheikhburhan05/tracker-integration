"use client"
import { useEffect, useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from '@/components/ui/table';
import { getJobs, getCandidates } from '../../api/api';
import { Job, Candidate } from '../../types/types';

export default function Dashboard() {
    const [jobs, setJobs] = useState<Job[]>([]);
    const [candidates, setCandidates] = useState<Candidate[]>([]);
    const [selectedJob, setSelectedJob] = useState<Job | null>(null);
    const [loading, setLoading] = useState<boolean>(false);

    const fetchJobs = async () => {
        try {
            setLoading(true);
            const jobsData = await getJobs();
            setJobs(jobsData);
        } catch (error) {
            console.error('Error fetching jobs:', error);
        } finally {
            setLoading(false);
        }
    };

    const fetchCandidates = async (jobId: string) => {
        try {
            setLoading(true);
            const candidatesData = await getCandidates(jobId);
            setCandidates(candidatesData);
        } catch (error) {
            console.error('Error fetching candidates:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleJobClick = (job: Job) => {
        setSelectedJob(job);
        fetchCandidates(job.id);
    };

    useEffect(() => {
        fetchJobs();
    }, []);

    return (
        <div className="container mx-auto p-4">
            <h1 className="text-2xl font-bold mb-4">ATS Dashboard</h1>
            <Button onClick={fetchJobs} className="mb-4" disabled={loading}>
                {loading ? 'Loading...' : 'Refresh Jobs'}
            </Button>

            <Card className="mb-8">
                <CardHeader>
                    <CardTitle>Job Posts</CardTitle>
                </CardHeader>
                <CardContent>
                    <Table>
                        <TableHeader>
                            <TableRow>
                                <TableHead>Title</TableHead>
                                <TableHead>Status</TableHead>
                                <TableHead>Job Type</TableHead>
                                <TableHead>Created At</TableHead>
                            </TableRow>
                        </TableHeader>
                        <TableBody>
                            {jobs.length > 0 ? (
                                jobs.map((job) => (
                                    <TableRow
                                        key={job.id}
                                        className="cursor-pointer hover:bg-gray-100"
                                        onClick={() => handleJobClick(job)}
                                    >
                                        <TableCell>{job.title}</TableCell>
                                        <TableCell>{job.status}</TableCell>
                                        <TableCell>{job.employmentType}</TableCell>
                                        <TableCell>{new Date(job.createdAt).toLocaleDateString()}</TableCell>
                                    </TableRow>
                                ))
                            ) : (
                                <TableRow>
                                    <TableCell colSpan={4} className="text-center">
                                        No jobs found.
                                    </TableCell>
                                </TableRow>
                            )}
                        </TableBody>
                    </Table>
                </CardContent>
            </Card>

            {selectedJob && (
                <Card>
                    <CardHeader>
                        <CardTitle>Candidates for {selectedJob.title}</CardTitle>
                    </CardHeader>
                    <CardContent>
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Name</TableHead>
                                    <TableHead>Email</TableHead>
                                    <TableHead>Stage</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {candidates.length > 0 ? (
                                    candidates.map((candidate) => (
                                        <TableRow key={candidate.id}>
                                            <TableCell>{candidate.name}</TableCell>
                                            <TableCell>{candidate.email}</TableCell>
                                            <TableCell>{candidate.stage}</TableCell>
                                        </TableRow>
                                    ))
                                ) : (
                                    <TableRow>
                                        <TableCell colSpan={3} className="text-center">
                                            No candidates found for this job.
                                        </TableCell>
                                    </TableRow>
                                )}
                            </TableBody>
                        </Table>
                    </CardContent>
                </Card>
            )}
        </div>
    );
}