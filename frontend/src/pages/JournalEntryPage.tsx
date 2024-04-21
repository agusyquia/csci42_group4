import React, {useEffect, useState} from 'react';
import {Link, useLocation} from 'react-router-dom';
import {AppShell, Burger, Container, Space, Stack, TextInput, Button, Grid, Select, Group} from '@mantine/core';
import { useDisclosure } from '@mantine/hooks';
import '../styles/JournalEntryPage.css';
import TextEditor from "../components/TextEditor";

function useQuery(): URLSearchParams {
    return new URLSearchParams(useLocation().search);
}

//export default function JournalEntryPage() {
const JournalEntryPage: React.FC = () => {
    let query = useQuery();
    const [date, setDate] = useState<string>('');
    const [content, setContent] = useState<string>('');
    const [selectedActivities, setSelectedActivities] = useState<string[]>([]); // State to track selected activities

    const handleContentChange = (newContent: string) => {
        setContent(newContent);
    };

    useEffect(() => {
        const dateParam = query.get('date');
        if (dateParam) {
            setDate(dateParam);
            const savedContent = localStorage.getItem(dateParam);
            if (savedContent) {
                setContent(savedContent);
            }
        }
    }, [query]);

    useEffect(() => {
        if (date) {
            const timer = setTimeout(() => {
                localStorage.setItem(date, content);
            }, 1000);

            return () => clearTimeout(timer);
        }
    }, [content, date]);

    const handleActivitySelect = (activity: string | null, option?: { value: string, label: string }) => {
        if (activity !== null && !selectedActivities.includes(activity)) {
            setSelectedActivities(prevActivities => [...prevActivities, activity]);
        }
    };


    return (
        <Grid>
            <Grid.Col span={6}>
                <h2>Journal Entry for {date}</h2>
                <TextEditor initialContent={content} onContentChange={handleContentChange} />
            </Grid.Col>
            <Grid.Col span={6}>
                <h2>Today I did...</h2>
                <Select
                    label="Choose activities"
                    placeholder="Activity"
                    data={['Activity1', 'Activity2', 'Activity3', 'Activity4']} // Data should ideally come from backend
                    searchable
                    onChange={handleActivitySelect}
                />
                <Group mt={10}>
                    {selectedActivities.map(activity => (
                        <Button key={activity}>{activity}</Button>
                    ))}
                </Group>
            </Grid.Col>
        </Grid>
    );
}

export default JournalEntryPage