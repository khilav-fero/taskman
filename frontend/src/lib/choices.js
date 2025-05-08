// lib/choices.js

// --- ADD ROLE CHOICES ---
export const Role = Object.freeze({ 
    ADMIN: 'ADMIN',
    MANAGER: 'MANAGER',
    TEAM_MEMBER: 'TEAM_MEMBER'
});

export const roleChoicesForSelect = [
    { value: Role.ADMIN, title: 'Admin' },
    { value: Role.MANAGER, title: 'Manager' },
    { value: Role.TEAM_MEMBER, title: 'Team Member' }
];
// --- END ADDITION ---


export const taskStatusChoices = [
    { value: 'TODO', title: 'To-Do' },
    { value: 'INPROGRESS', title: 'In-Progress' },
    { value: 'REVIEW', title: 'Code Review' },
    { value: 'DONE', title: 'Done' },
];

export const taskPriorityChoices = [
    { value: 1, title: 'Low' },
    { value: 2, title: 'Medium' },
    { value: 3, title: 'High' },
    { value: 4, title: 'Urgent' },
];

export const getStatusTitle = (value) => {
    return taskStatusChoices.find(c => c.value === value)?.title || value;
};

export const getPriorityTitle = (value) => {
    const numValue = Number(value);
    return taskPriorityChoices.find(c => c.value === numValue)?.title || value;
};