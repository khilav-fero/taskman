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