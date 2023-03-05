# from django.shortcuts import render
from api.serializers.doctor_serializer import (
    HospitalSerializer,
    SpecialtySerializer,
)
from api.services.get_doctor_service import get_doctor
from rest_framework import serializers, status
from rest_framework.response import Response
from rest_framework.views import APIView
from utils.text_processing import give_disease, is_input_valid


class PredictDoctorView(APIView):
    class InputSerializer(serializers.Serializer):
        noOfDoctors = serializers.IntegerField()
        symptoms = serializers.CharField()

    class OutputSerializer(serializers.Serializer):
        name = serializers.CharField()
        specialty = SpecialtySerializer()
        phone_number = serializers.CharField()
        email = serializers.CharField()
        hospital = HospitalSerializer()

    def post(self, request, *args, **kwargs):
        result = []
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        symptoms = request.data["symptoms"]
        if not is_input_valid(symptoms):
            return Response(
                data={"data": "Please enter valid text"},
                status=status.HTTP_200_OK,
            )

        diseases = give_disease(input_text=symptoms)
        print(diseases)
        if not diseases:
            return Response(
                data={
                    "data": "Sorry we couldn't find you a doctor. Please Sorry for inconvenience."
                },
                status=status.HTTP_200_OK,
            )
        for disease in diseases:
            queryset = get_doctor(disease)
            if queryset:
                serializer = self.OutputSerializer(queryset)
                result.append(serializer.data)

        # print(result)
        return Response(data={"data": result}, status=status.HTTP_200_OK)
        # return Response({"data": diseases}, status.)
