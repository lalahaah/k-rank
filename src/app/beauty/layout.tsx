import { Metadata } from 'next';
import { beautyMetadata } from './metadata';

export const metadata: Metadata = beautyMetadata;

export default function BeautyLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return <>{children}</>;
}
