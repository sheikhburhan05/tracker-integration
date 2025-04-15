export interface Job {
    id: string;
    title: string;
    status: string;
    employmentType: string;
    createdAt: string;
}

export interface Candidate {
    id: string;
    name: string;
    email: string;
    stage: string;
}