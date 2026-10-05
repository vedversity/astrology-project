import { MuhuratPage, muhuratMetadata } from "@/components/muhurat";

type Props = { params: Promise<{ type: string; year: string }> };

export async function generateMetadata({ params }: Props) {
  const { type, year } = await params;
  return muhuratMetadata("en", type, year);
}

export default async function Page({ params }: Props) {
  const { type, year } = await params;
  return <MuhuratPage lang="en" type={type} year={year} />;
}
