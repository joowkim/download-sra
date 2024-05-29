nextflow.enable.dsl=2

process down_sra {
    tag "downloading_SRA"

    cpus 4
    memory "8 GB"

    publishDir "${launchDir}/analysis/SRA", mode: "copy"

    module "sratoolkit/3.0.0"

    input:
    val(sra_id)

    output:
    path("*.gz")

    script:
    // --split-files for PE data
    """
        fasterq-dump --split-files ${sra_id}
        pigz ${sra_id}*.fastq
    """
}

ch_samplesheet = Channel.fromPath(params.samplesheet, checkIfExists: true)
ch_sra = ch_samplesheet.splitCsv(header:true).map {

    // This is the read1 and read2 entry
    sra_id = it['sra_id']
}

workflow {
    down_sra(ch_sra)
}

workflow.onComplete {
	println ( workflow.success ? "\nDone!" : "Oops .. something went wrong" )
}