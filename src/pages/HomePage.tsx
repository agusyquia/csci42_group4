//Source: https://mantine.dev/app-shell/?e=CollapseDesktop&s=code
import { useState } from 'react';
import { AppShell, Burger, Container, Space, Group, Stack, Collapse } from '@mantine/core';
import { DatePicker, DatePickerProps, Day  } from '@mantine/dates';
import { useDisclosure } from '@mantine/hooks';
import { Link } from 'react-router-dom';
import './HomePage.css';


export default function HomePage() {
    const [value, setValue] = useState<Date | null>(null);
    const [opened, { toggle: toggleDesktop }] = useDisclosure();

    return (
        <AppShell
            layout='alt'
            header={{ height: 60}}
            aside={{ 
                width: 500, 
                breakpoint: 'md',   
                collapsed: {desktop: !opened }
            }}
            padding="md"
        >
        <AppShell.Header withBorder={false} bg='coffee.5'>
            <Group h="100%" px="md" justify='flex-end'>
                <Burger opened={opened} onClick={toggleDesktop} visibleFrom="sm" size="md" color='white' mt= '25' mr='100'/>
            </Group>
        </AppShell.Header>

        <AppShell.Aside bg = 'coffee.3' p="md">
            <Stack align='center' justify='center' gap='xl'>
                <Burger
                    opened={opened} 
                    onClick={toggleDesktop} 
                    visibleFrom="sm" 
                    size="md" 
                    color='white' 
                    mt= '10' 
                    ml='240'
                    bg={'coffee.5'}
                />
                <Link to ="/" className='link'>Homepage</Link>
                <Link to ="/" className='link'>Journal Entry</Link>
                <Link to ="/" className='link'>Activity</Link>
                <Link to ="/" className='link'>Timer</Link>
                <Link to ="/" className='link'>Activity Creation</Link>
                <Link to ="/" className='link'>Summary</Link>
            </Stack>
        </AppShell.Aside>

        <AppShell.Main>
            <div style={{position: 'fixed', top: '100px',left: '200px'}}>
                    <DatePicker 
                        allowDeselect
                        value={value}
                        onChange={setValue}
                        maxLevel="month"
                        size='xl'
                        monthLabelFormat="MMMM"
                        // bg={'cyan'}
                        styles={{
                            day: {
                                color: '#543f3f',
                                backgroundColor: '#ead8c2',
                            }
                        }}
                    />
            </div>
            <div style={{position: 'fixed', top: '100px', left: '800px'}}>
                <h2>Journal of</h2>
                <h1>USERNAME :D</h1>
            </div>

        </AppShell.Main>
    </AppShell>
  );
}