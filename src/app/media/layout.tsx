import { Metadata } from 'next';
import { mediaMetadata } from './metadata';

export const metadata: Metadata = mediaMetadata;

export default function MediaLayout({
    children,
}: {
    children: React.ReactNode;
}) {
    return <>{children}</>;
}
