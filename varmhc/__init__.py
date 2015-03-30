from collections import defaultdict
import pandas as pd
from mhctools import NetMHCpan


def predict(variant_collection,
            hla_alleles,
            predictor_type='netmhcpan',
            epitope_lengths=[9],
            mutation_window_size=None,
            raise_on_error=False):
    if predictor_type == 'netmhcpan':
        predictor = NetMHCpan(hla_alleles,
                  netmhc_command='netMHCpan',
                  epitope_lengths=epitope_lengths)
        df = _create_dataframe(
            variant_collection=variant_collection,
            hla_alleles=hla_alleles,
            predictor_type=predictor_type,
            epitope_lengths=epitope_lengths,
            mutation_window_size=mutation_window_size,
            raise_on_error=raise_on_error)
        return predictor.predict(
            df, mutation_window_size=mutation_window_size)
    else:
        raise ValueError('Unsupported predictor: %s' % predictor)


def _create_dataframe(variant_collection,
                      hla_alleles,
                      predictor_type,
                      epitope_lengths,
                      mutation_window_size,
                      raise_on_error):
    df_lists = defaultdict(list)
    for variant in variant_collection:
        for effect in variant.effects(raise_on_error=raise_on_error):
            try:
                # Skip over non-coding mutations (and unpredictable
                # coding mutations)
                mutation_start = effect.mutation_start
                mutation_end = effect.mutation_end
                source_sequence = effect.mutant_protein_sequence
            except Exception as e:
                if raise_on_error:
                    raise e
                continue

            df_lists['chr'].append(variant.contig)
            df_lists['pos'].append(variant.start)
            df_lists['ref'].append(variant.ref)
            df_lists['alt'].append(variant.alt)
            df_lists['MutationStart'].append(mutation_start)
            df_lists['MutationEnd'].append(mutation_end)
            df_lists['SourceSequence'].append(source_sequence)
            df_lists['GeneInfo'].append(None)
            df_lists['Gene'].append(effect.gene_name())
            df_lists['GeneMutationInfo'].append(variant.short_description())
            df_lists['PeptideMutationInfo'].append(effect.short_description())
            df_lists['TranscriptId'].append(effect.transcript.id)
    return pd.DataFrame(df_lists)
