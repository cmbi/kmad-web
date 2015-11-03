
"""
This example client takes a FASTA sequence, sends it to the service, which
performs prediction and alignment.
The output is sent to the command line.

Example:

    python predict_and_align.py TAU_HUMAN.fasta http://www.cmbi.umcn.nl/kmad-web/ predict_and_align
"""

import argparse
import json
import requests
import time


def kmad(sequence_path, kmad_url, output_type):
    # Read the fasta file data into a variable
    with open(sequence_path) as fasta_file:
        fasta_content = fasta_file.read()

    # Send a request to the server to perform disorder prediction and alignment
    # with homologous sequences.
    # If an error occurs, an exception is raised and the program exits. If the
    # request is successful, the id of the job running on the server is
    # returned.
    url_create = '{}api/create/{}/'.format(kmad_url,
                                           output_type)
    print url_create
    r = requests.post(url_create, data={'data': fasta_content})
    r.raise_for_status()

    job_id = json.loads(r.text)['id']
    print "Job submitted successfully. Id is: '{}'".format(job_id)

    # Loop until the job running on the server has finished, either successfully
    # or due to an error.
    ready = False
    while not ready:
        # Check the status of the running job. If an error occurs an exception
        # is raised and the program exits. If the request is successful, the
        # status is returned.
        url_status = '{}api/status/{}/{}/'.format(kmad_url,
                                                  output_type,
                                                  job_id)
        r = requests.get(url_status)
        r.raise_for_status()

        status = json.loads(r.text)['status']
        print "Job status is: '{}'".format(status)
        # If the status equals SUCCESS, exit out of the loop by changing the
        # condition ready. This causes the code to drop into the `else` block
        # below.
        #
        # If the status equals either FAILURE or REVOKED, an exception is raised
        # containing the error message. The program exits.
        #
        # Otherwise, wait for five seconds and start at the beginning of the
        # loop again.
        if status == 'SUCCESS':
            ready = True
        elif status in ['FAILURE', 'REVOKED']:
            raise Exception(json.loads(r.text)['message'])
        else:
            time.sleep(5)
    else:
        # Requests the result of the job. If an error occurs an exception is
        # raised and the program exits. If the request is successful, the result
        # is returned.
        url_result = '{}api/result/predict/{}/'.format(kmad_url,
                                                       job_id)
        r = requests.get(url_result)
        r.raise_for_status()
        result = json.loads(r.text)['result']

        # Return the result to the caller, which prints it to the screen.
        return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Predict disorder')
    parser.add_argument('sequence_path')
    parser.add_argument('kmad_url')
    parser.add_argument('output_type')
    args = parser.parse_args()

    result = kmad(args.sequence_path, args.kmad_url, args.output_type)
    print result
